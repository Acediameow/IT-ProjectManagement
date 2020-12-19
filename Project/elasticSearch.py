import csv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class ElasticObj:
    def __init__(self, index_name, index_type, ip="127.0.0.1"):  # 初始化
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch([ip], timeout=60)

    def create_index(self, index_name="ott", index_type="_doc"):
        # 创建映射
        _index_mappings = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                    },
                    "time": {
                        "type": "date",
                        "format": "yyyy-MM-dd HH:mm:ss"
                    },
                    "url": {
                        "type": "text"
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "ik_smart",
                        "search_analyzer": "ik_smart",
                        "fielddata": True,
                    },
                    "sentiment": {
                        "type": "text",
                    }
                }
            }
        }
        if self.es.indices.exists(index=self.index_name) is not True:
            res = self.es.indices.create(index=self.index_name, body=_index_mappings)
            print(res)

    def Get_data(self, csvfile):
        f = open(csvfile, 'r', encoding='utf-8')
        csvreader = csv.reader(f)
        l = list(csvreader)
        return l

    def Index_Data_FromCSV(self, csvfile):  # 从csv读取数据存到es中(bulk)
        l = self.Get_data(csvfile)
        ACTIONS = []
        index = 0
        for line in l:
            index = index + 1
            if index % 5000 == 0:  # 分批次处理
                success, _ = bulk(self.es, ACTIONS, index=self.index_name)
                ACTIONS = []
                print('Performed %d actions' % success)
            if index > 1:
                action = {
                    "_index": self.index_name,
                    "_type": "_doc",
                    "_id": index,
                    "_source": {
                        "title": line[0],
                        "time": line[1],
                        "url": line[2],
                        "content": line[3],
                        "sentiment": line[4]
                    }
                }
                ACTIONS.append(action)
        if (len(ACTIONS) > 0):
            bulk(self.es, ACTIONS, index=self.index_name)

    def Get_Data_By_Body(self, stype, where, word):  # 搜索
        doc = {
            "query": {
                stype: {
                    where: word,
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc, params={"size": 1000})
        return _searched['hits']['hits']

    def Delete_of_all(self):  # 清空
        body = {
            "query": {
                "match_all": {}
            }
        }
        res = self.es.search(index=self.index_name, body=body)
        self.es.delete_by_query(index=self.index_name, body=body)
        print("清空完成")

    def Delete_Index(self, my_index):
        self.es.indices.delete(index=my_index, ignore=[400, 404])

    def Get_data_time(self, date1, date2, word):  # 每天的关键词的情感趋势
        doc = {
            "query": {
                "bool": {
                    "must": [{
                        "range": {
                            "time": {
                                "from": date1,
                                "to": date2
                            }
                        }
                    },
                        {
                            "match": {
                                "content": word,
                            }
                        }]
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc, params={"size": 1000})
        return _searched['hits']['hits']

    def Get_data_time_sentiment(self, date1, date2, word, sen):  # 每天的关键词的情感趋势
        doc = {
            "query": {
                "bool": {
                    "must": [{
                        "range": {
                            "time": {
                                "from": date1,
                                "to": date2
                            }
                        }
                    },
                        {
                            "match": {
                                "content": word,
                            }
                        },
                        {
                            "match": {
                                "sentiment": sen,
                            }
                        },
                    ]
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc, params={"size": 1000})
        return _searched['hits']['hits']

    def Hot_words_time(self, date1, date2):  # 根据日期挑选热词
        doc = {
            "aggs": {
                "date_ranges": {
                    "range": {
                        "field": "time",
                        "ranges": [
                            {
                                "from": date1,
                                "to": date2
                            },
                        ]},
                    "aggs": {
                        "content": {
                            "terms": {
                                "field": "content",
                                "size": 50,
                                "order": [{"_count": "desc"}]
                            }
                        }
                    }
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc)
        return _searched['aggregations']['date_ranges']['buckets'][0]['content']['buckets']
