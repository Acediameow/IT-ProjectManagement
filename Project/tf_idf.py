import re
import csv
import pandas as pd
import numpy as np
import jieba
import jieba.analyse


def tf_idf_cal(name):
    # 加载数据 
    p = 'dataset/' + name + '.csv'
    fa = open(p, encoding="utf_8", errors='ignore')
    fp = open('jieba/sentence_train_' + name + '.csv', 'a', newline='', encoding='utf-8-sig')
    writer = csv.writer(fp)
    dataset = pd.read_csv(fa)
    #dataset.drop_duplicates(["正文内容"], keep='first')
    data = np.array(dataset["正文内容"])

    # 所有标题的高频词情况
    # ------------------------------------中文分词------------------------------------
    cut_words = ""
    X = []
    for i in range(len(data)):
        try:
            data[i] = re.sub('[0-9’!"#$%&\'()*+,-./:：;<=>?@，。?…★、【】《》？“”‘’！[\\]^_`{|}~\s]+', "", data[i])
            if data[i] != "":
                seg_list = jieba.cut(data[i], cut_all=False)
                cut_word = (" ".join(seg_list))

                cut_words += cut_word
                n = []
                X.append(n)
                n.append(cut_word)
            writer.writerow(n)
        except:
            print("第%s行数据有误" % i)

    keywords = jieba.analyse.extract_tags(cut_words,
                                          topK=50,
                                          withWeight=True,
                                          allowPOS=('a', 'e', 'n', 'nr', 'ns', 'v'))  # 词性 形容词 叹词 名词 动词

    # keyword本身包含两列数据
    pd.DataFrame(keywords, columns=['词语', '重要性']).to_csv('jieba/TF_IDF关键词' + name + '.csv')
    return keywords
