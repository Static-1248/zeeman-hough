# 塞曼效应光谱环的OpenCV算法检测

在塞曼效应的观测实验中，使用OpenCV的HoughCircles算法对拍摄的光谱环照片进行分析，准确测定圆环的位置和大小，从而提高相关物理量的计算精度。

## 程序依赖

在conda环境下安装以下Python依赖：

```bash
conda activate phylab25xd                       # 激活已配置的conda环境

conda install -c conda-forge opencv             # OpenCV
conda install jupyter notebook                  # jupyter notebook
conda install numpy matplotlib                  # matplotlib可视化
conda install -c conda-forge ipywidgets ipympl  # jupyter notebook + matplotlib 的交互式可视化
```

Jupyter Lab 服务器需安装：

```bash
conda install -c conda-forge jupyterlab jupyter-collaboration
```

## HoughCircles算法笔记

```python
circles = cv2.HoughCircles(
    gray_img,           # 输入图像，需为单通道灰度图
    cv2.HOUGH_GRADIENT, # 检测方法, （可以试试另一个算法 cv2.HOUGH_GRADIENT_ALT？
    dp=1,              
    minDist=50,        
    param1=50,         
    param2=30,         
    minRadius=10,      
    maxRadius=300      
)
```

**参数说明**：

- `dp`：控制累加器分辨率的参数，`dp`字面意义，代表累加器网格里一个长度单位对应原图像的多少像素长度；
    - `dp=1`表示累加器网格与原图像分辨率一致，`dp=0.5`表示累加器网格的分辨率是原图像的2倍；
    - 值越小，累加器网格相对原图像越密；
- `minDist`：控制检测到的圆之间的最小距离，根据图像中圆环的密集程度调整
- `param1`：内部调用Canny边缘检测算法的高阈值(maxVal)参数，低阈值(minVal)参数取其1/2，影响边缘检测的灵敏度
- `param2`：累加器投票数阈值，一个点位需要多少投票才能被认定为圆心；值越小检测到的圆越多（可能包含更多误检），值越大检测越严格。
- `minRadius`和`maxRadius`：检测圆的最小和最大半径；
    1. 影响累加过程，每个边缘点会在其法线两侧距离其[minRadius, maxRadius]的线段范围内投票一次；
    2. 影响半径估计，对于每个圆心，取Canny边缘检测结果二值图中距离圆心[minRadius, maxRadius]圆环区域内的边缘点统计半径。

注：
- c++ 源码里的隐藏参数：
    - `param3`参数，控制Canny/Sobel算法的kernalSize。调用值为3。
    - `maxCircles`参数，控制返回的圆心个数。调用值为-1。
    - 源码里有一个带这些参数的函数以及一个没有这些参数的函数。OpenCV将后者开放使用，后者的函数体内部使用上述的调用值调用前者。
- `minRadius` 下限为0；
- `maxRadius <= 0` 时 `maxRadius` 取图像宽高最大值；
- `maxRadius <= minRadius` 时 `maxRadius` 取 `minRadius + 2`；
- `maxRadius < 0` 时 `centerOnly` 设为 `True`，只检测圆心，不估计半径； 

**算法原理**：

算法对图像进行4个步骤的处理：Canny边缘检测、圆心投票、圆心筛选、圆半径估计
1. **Canny边缘检测**：对输入图像进行Canny边缘检测，得到二值图像。
    - 该步骤使用`cv2.Canny()`函数，参数为输入图像、低阈值和高阈值。
    - 高阈值设为`param1`，低阈值设为`param1/2`（下限为1）
    - 该步骤中计算出：
        - `edges`：二值图像，边缘点为255，非边缘点为0
        - `dx`：图像在x方向的梯度值图像，Sobel算子的计算结果
        - `dy`：图像在y方向的梯度值图像，Sobel算子的计算结果

2. **圆心投票**：让每个边缘点进行投票，计算其可能的圆心位置。
    - 对于每个边缘点，在其法线（法线方向根据 `dx`和`dy` 梯度值计算）直线经过的所有点上都+1一次（留下一道痕迹）；这样理论上在圆心处投票数最多。
    - 实际上并未在直线的全部范围内投票，而是只在边缘点两侧的[minRadius, maxRadius]线段范围内投票。
    - 投票时是在累加器网格上投票，累加器网格与原图像的分辨率可以不一致，由`dp`参数控制。`dp`代表累加器网格的一个长度单位对应原图像的多少像素长度。
    - 实际算法是：在法线一侧令半径以 minRadius 为起点，maxRadius 为终点，dp 为步长逐步遍历半径，对半径计算出精确的投票点坐标，并计算其在累加器网格上的投影坐标，+1投票。算法内投票点的坐标为整型，但做了*1024倍处理，所以坐标精度为1/1024像素。
    - 该步骤中计算出：
        - `accum`：累加器，投票结果
        - `nz`：`edges`的另一种表示，以点坐标列表的形式存储所有在`edges`图像里非零值的有效边缘点

3. **圆心筛选**：对投票结果进行筛选，找到可能的圆心位置。
    - 对于每个投票点，计算其在累加器中的投票数，如果投票数大于`param2`，则认为该点为圆心。
    - 圆心列表按照累加得票数从大到小排序。
    - 该步骤中计算出：
        - `centers`：可能的圆心位置列表

4. **圆半径估计**：对每个圆心位置估计其半径，获得完整的圆检测结果。
    - 对于每个圆心位置，对其在`edges`图像（实际上是取`nz`边缘点列表）中距离圆心[minRadius, maxRadius]范围内的边缘点进行统计；
    - 进行半径的区间频数统计，取“频数/半径值”最大的区间中值作为该圆心的半径。
    - 区间划分为： `[minRadius, maxRadius]` 范围内划分出若干个长度为`dr=dp`的大区间，每个大区间内划分`nBinsPerDr = 10`个小区间；
    - 统计每个小区间内的边缘点个数，然后求和到大区间上，取“频数/半径值”最大的区间中值作为该圆心的半径；
    - 实际上还用`param2`阈值与频数进行比较，频数小于阈值则该圆心被认为无效。

    - 对所有圆心进行半径估计后，对它们进行排序：频数大者优先，半径大者优先，X坐标小者优先，Y坐标小者优先。
    - 排序后移除过分重合的圆心，受`minDist`控制。在排序后的圆列表中，依次让每个圆心与前面所有圆心进行距离比较，确保它们之间的距离大于`minDist`，否则移除当前圆心。
    - （最后取前`maxCircles`个圆心作为最终结果。）

    若 `centerOnly` 设为 `True`，只检测圆心，则流程为：
    - 移除过分重合的圆心，同前面所述；受`minDist`控制。
    - 返回圆列表时半径设为0。
    
    - 该步骤中计算出：
        - `circles`：可能的圆的完整数据列表
        - `circles`的格式为：`[[x, y, r], ...]`，其中`x`和`y`为圆心坐标，`r`为半径


## 参考网址

**OpenCV 官方文档：**

- 两篇教程+接口文档：
    - [OpenCV: Hough Circle Transform](https://docs.opencv.org/3.4/da/d53/tutorial_py_houghcircles.html)
    - [OpenCV: Hough Circle Transform](https://docs.opencv.org/4.11.0/d4/d70/tutorial_hough_circle.html)
    - `HoughCircles()` 文档：[OpenCV: Feature Detection](https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga47849c3be0d0406ad3ca45db65a25d2d)

- 其他相关算法文档：
    - 模糊图像：[OpenCV: Smoothing Images](https://docs.opencv.org/3.4/d4/d13/tutorial_py_filtering.html)
    - `medianBlur()`：[OpenCV: Image Filtering](https://docs.opencv.org/4.11.0/d4/d86/group__imgproc__filter.html#ga564869aa33e58769b4469101aac458f9)
    - Canny边缘检测：[OpenCV: Canny Edge Detection](https://docs.opencv.org/4.11.0/d7/de1/tutorial_js_canny.html)

**其他网络资源：**

- [Hough Transform using OpenCV](https://learnopencv.com/hough-transform-with-opencv-c-python/)

> 注：以下4篇与OpenCV实现关联性较弱，仅介绍Hough Circle Transform算法原理
- [Hough Circle Transform using OpenCV](https://medium.com/@isinsuarici/hough-circle-transform-in-opencv-d74bdf5161ed)
- [Circle Hough Transform - Wikipedia](https://en.wikipedia.org/wiki/Circle_Hough_Transform)
- [How Circle Hough Transform works - Youtube](https://www.youtube.com/watch?v=Ltqt24SQQoI)
- [Hough Circle Transform - 知乎](https://zhuanlan.zhihu.com/p/427065017)

- [How-to Guides --- Jupyter Widgets](https://ipywidgets.readthedocs.io/en/latest/how-to/index.html)

**HoughCircles源码：**

- [OpenCV Github](https://github.com/opencv/opencv/blob/90e7119ce025983f0ffbd0d2187b3cb1b8279b32/modules/imgproc/src/hough.cpp#L2357)