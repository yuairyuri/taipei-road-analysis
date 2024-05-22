# 臺北市道路分析

## 研究計畫

主張：以人為本，改善都市用路人權以及環境綠化

近年來，臺北市發展迅速，道路、建案和公共設施的開發促進都市經濟繁榮，為居民提供便利的生活環境。但是，這也導致**行人環境惡化**、**綠帶縮減**等問題的發生。

主要議題：

1. 行人環境改善
2. 增加綠化

## 資料收集

資料來源：[臺北市資料大平臺](https://data.taipei/)

| 資料名稱 | Provider | Link |
| ------- | -------- | ---- |
| 臺北市寬度超過8公尺道路GIS圖資 | 新工處 | [here](https://data.taipei/dataset/detail?id=ee2e4015-8844-48fb-aa57-31209909b0fc) |
| 臺北市人行道固定設施物_人行道範圍圖 | 新工處 | [here](https://data.taipei/dataset/detail?id=715d3a83-8445-4496-b6bf-b0900538b7e7) |
| 臺北市行道樹分布圖 |公燈處 | [here](https://data.taipei/dataset/detail?id=7a49d00c-a5ff-4a6b-be9e-aaa6dc1ff7e8) |
| 臺北捷運車站出入口座標 | 捷運公司 | [here](https://data.taipei/dataset/detail?id=cfa4778c-62c1-497b-b704-756231de348b) |
| 臺北市公車站牌位置圖 | 公運處 | [here](https://data.taipei/dataset/detail?id=48aa5bca-2a4f-4fb7-a658-43cba51d5d56) |
| YouBike2.0臺北市公共自行車即時資訊 | 交通局 | [here](https://data.taipei/dataset/detail?id=c6bc8aed-557d-41d5-bfb1-8da24f78f2fb) |

資料來源：[Open Street Map](https://www.openstreetmap.org)

| 資料名稱 | Provider | Link |
| ------- | -------- | ---- |
| Points of Interest | OSM  | [here](https://download.geofabrik.de/asia/taiwan.html#)

## 分析方法

軟體工具：

* Excel

* QGIS

* Python

### GIS 空間分析

各路段人行道寬度的計算：

1. 新增`寬度超過8公尺以上道路`、`臺北市人行道`圖層

2. 新增`道路`的 Buffer (distance = 12 meters)

3. 取道路的`Buffer`和`人行道`的交集

4. 計算同一側人行道的平均寬度

5. 將東西側、南北側的人行道寬度分別加總

6. 依道路方向（南北向、東西向）指派該路段的人行道寬度

各路段行道樹密度的計算：

使用 **Count Points in Polygon** 演算法，計算`道路`的每個路段上`行道樹`的數量，再除以路段面積。

人流量的估計：

取用 POI 資料中的電影院、餐廳、商場等商業活動場所，作為可能的人群聚集地，以此推估人流量。

1. 新增`POI`的 Heatmap (Kernel Density Estimation)

2. **Zonal Statistics**

3. 取路段內像素值的平均作為人流量大小的估計值

## About Us

National Taipei University of Technology

Group D of Urban Data Science Course