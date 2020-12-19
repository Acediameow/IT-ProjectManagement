# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 14:34:42 2020

@author: lenovo
"""
from pyecharts import options as opts
from pyecharts.charts import Pie


def pie_base(data1, data2) -> Pie:
    list_color = ['#990033', '#990000', '#CC0066', '#CC0033', '#CC0000', '#FF0000', 'FF00FF', 'FF1493', '#FF4500',
                  '#FF6347']
    pie = Pie()
    pie.add(
        series_name="",
        data_pair=[list(z) for z in zip(data1, data2)],
        radius=["20%", "75%"],
        rosetype="area",
        label_opts=opts.LabelOpts(is_show=False),
    )
    pie.set_colors(list_color)
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title="", title_textstyle_opts=(opts.TextStyleOpts(color='white'))),
        legend_opts=opts.LegendOpts(is_show=False))

    return pie
