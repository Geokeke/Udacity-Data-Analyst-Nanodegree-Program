# 创建有效的数据可视化

最初可视化见[这里](http://bl.ocks.org/Geokeke/raw/9a67de201d8146ef66a23eb6c4edcb35/)

改进的可视化在[这里](http://bl.ocks.org/Geokeke/raw/b828fad56084950d9074a521a88a836e/)

## 概要

本项目是关于2008年美国国内航班准点和延误情况的可视化。我从[美国统计协会](http://stat-computing.org/dataexpo/2009/the-data.html)下载2008年美国航班的数据集并清洗整理，最后做成环状图，反应该年度四个季度的准点率、航班延误的原因及其比例。


## 设计

本可视化项目计划回答如下问题：

1. 2008年全年及各季度，美国航班的准点率如何？
2. 2008年全年及各季度，美国航班的延误率如何？航班延误的原因有什么，各占多少百分比？
3. 季度不同，准点率、延误原因及比率是否会显著不同？

要回答这些问题，我认为最合适的可视化是饼图或环形图，它们通过颜色来标识准点及延误原因，用角度（面积）代表准点航班和各延误原因所占百分比可以回答上述问题。另外，我认为环形图比饼图更简洁优美，故选择环形图完成此次可视化。

通过此次可视化可以发现：

1. 2008年，美国全年平均准点率78%，各季度准点率也在这个值左右，最小值是第一季度73%，最大第三季度81%；
2. 全年延误率22%，各季度延误率也在这个值左右，最大值是第一季度27%，最小第三季度19%。延误原因主要有Aircraft Arriving Late和National Aviation System Delay，此外还有Air Carrier Delay、Cancelled & Diverted、Extreme Weather、Security Delay，所占百分比依次降低；
3. 季度不同，准点率、延误原因及比率比较接近，没有显著变化。

## 反馈

### [lemontechmaster (DAND Forum Mentor)](https://discussions.youdaxue.com/u/lemontechmaster)

他回答了几个问题：

1. 你在这个可视化中注意到什么？

   大部分航班都是准点的。

2. 你对这个数据有什么问题吗？

   除了大部分航班都是准点的这个信息外，其他的信息第一时间读不出来，你想要分享的故事（结论）是什么呢？

3. 你是否注意到数据关系？

   On Time
   Aircraft Arriving Late
   National Aviation System Delay
   Air Carrier Delay
   Cancelled & Diverted
   Extreme Weather
   Security Delay
   占比依次递减。

4. 你觉得这个可视化主要表达了什么？

   大部分航班是准点的，以及常见的航班延误原因。

5. 这个图形中你有什么不明白的地方吗？

   无。

并给出了建议：4个图能否放置成2*2的矩阵排列呢？备注的文字信息能否再精简一些？

### 源

1. 只看图例，不能够了解各延误原因的具体含义，可在下面添加解释；
2. 四张图这样排列不易于查看比较，最好做成带按钮的，点击哪个季度，显示哪个季度的图表。

### Kirsch

这个可视化很直观地表现了准点率、航班延误原因及所占比率，一目了然。我注意到四张环状图各表现了四个季度的情况，但没有全年的可视化。可否将全年的加上？



## 资源

- http://dimplejs.org/
- https://d3js.org/
- [Data](http://stat-computing.org/dataexpo/2009/the-data.html)

