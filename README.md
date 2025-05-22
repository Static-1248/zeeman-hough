# 塞曼效应光谱环的 OpenCV 检测算法

本项目旨在通过 OpenCV 的 HoughCircles 算法，对塞曼效应实验中拍摄的光谱环照片进行自动分析，精准测定圆环的位置和大小，从而提升相关物理量的计算精度。

## 环境依赖

建议在 conda 环境下安装以下 Python 依赖：

```bash
conda activate phylab25xd                       # 激活已配置的 conda 环境
conda install -c conda-forge opencv             # OpenCV
conda install jupyter notebook                  # Jupyter Notebook
conda install numpy matplotlib scipy            # 科学计算与可视化
conda install -c conda-forge ipywidgets         # 交互式可视化支持
```

如需使用 Jupyter Lab 服务器：

```bash
conda install -c conda-forge jupyterlab jupyter-collaboration
```

## HoughCircles算法笔记

### 基本用法

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

### 参数说明

- `dp`：控制累加器分辨率的参数，`dp`字面意义，代表累加器网格里一个长度单位对应原图像的多少像素长度；
    - `dp=1`表示累加器网格与原图像分辨率一致，`dp=0.5`表示累加器网格的分辨率是原图像的2倍；
    - 值越小，累加器网格相对原图像越密；
- `minDist`：控制检测到的圆之间的最小距离，根据图像中圆环的密集程度调整。
- `param1`：内部调用Canny边缘检测算法的高阈值(maxVal)参数，低阈值(minVal)参数取其1/2，影响边缘检测的灵敏度。
- `param2`：累加器投票数阈值，一个点位需要多少投票才能被认定为圆心；值越小检测到的圆越多（可能包含更多误检），值越大检测越严格。
- `minRadius`和`maxRadius`：检测圆的最小和最大半径；
    1. 影响累加过程，每个边缘点会在其法线两侧距离其[minRadius, maxRadius]的线段范围内投票一次；
    2. 影响半径估计，对于每个圆心，取Canny边缘检测结果二值图中距离圆心[minRadius, maxRadius]圆环区域内的边缘点统计半径。

**源码细节与补充说明：**
- C++ 源码里的隐藏参数：
    - `param3`参数，控制Canny/Sobel算法的kernalSize。调用值为3。
    - `maxCircles`参数，控制返回的圆心个数。调用值为-1。
    - 源码里有一个带这些参数的函数以及一个没有这些参数的函数。OpenCV将后者开放使用，后者的函数体内部使用上述的调用值调用前者。
- `minRadius` 下限为0；
- `maxRadius <= 0` 时 `maxRadius` 取图像宽高最大值；
- `maxRadius <= minRadius` 时 `maxRadius` 取 `minRadius + 2`；
- `maxRadius < 0` 时 `centerOnly` 设为 `True`，只检测圆心，不估计半径； 

---

### 算法原理与实现细节

HoughCircles 算法对图像的处理主要分为四个步骤：Canny 边缘检测、圆心投票、圆心筛选、圆半径估计。

#### 1. Canny 边缘检测
- 首先对输入图像进行 Canny 边缘检测，得到二值化的边缘图像。
    - 使用 `cv2.Canny()`，高阈值为 `param1`，低阈值为 `param1/2`（下限为1）。
    - 该步骤会得到：
        - `edges`：二值图像，边缘点为255，非边缘点为0。
        - `dx`、`dy`：分别为图像在 x、y 方向的梯度（Sobel 算子计算结果），用于后续法线方向的计算。

#### 2. 圆心投票
- 对每个边缘点，沿其法线方向（由 `dx`、`dy` 决定）在[minRadius, maxRadius]范围内进行圆心投票。
    - 理论上，圆心处的投票数最多。
    - 实际投票只在边缘点两侧[minRadius, maxRadius]的线段范围内进行。
    - 投票是在累加器网格上完成，网格分辨率由 `dp` 控制（`dp=1` 表示与原图一致，`dp<1` 表示更密集）。
    - 实际算法是：以 `dp` 为步长，逐步遍历[minRadius, maxRadius]范围内的所有半径，对每个半径计算出精确的投票点坐标，并将其投影到累加器网格上进行投票。
    - 算法内部对投票点坐标做了 *1024 精度处理，即所有坐标都乘以 1024 后再取整，坐标精度达 1/1024 像素，这样可以保证亚像素级别的累加精度。
    - 该步骤会得到：
        - `accum`：累加器，记录投票结果。
        - `nz`：所有有效边缘点的坐标列表（`edges` 的非零点）。

#### 3. 圆心筛选
- 对累加器中的投票结果进行筛选，找出可能的圆心。
    - 若某点投票数大于 `param2`，则视为圆心候选。
    - 圆心候选按得票数从高到低排序。
    - 该步骤会得到：
        - `centers`：可能的圆心位置列表。

#### 4. 圆半径估计
- 对每个圆心位置，统计其在 `edges` 图像（实际上是取 `nz` 边缘点列表）中、距离圆心在[minRadius, maxRadius]范围内的边缘点。
    - 将[minRadius, maxRadius]区间划分为若干长度为 `dr=dp` 的大区间，每个大区间再细分为 10 个小区间。
    - 统计每个小区间内的边缘点数，累加到大区间。
    - 取"频数/半径值"最大的区间的中值作为该圆心的半径。
    - 若该区间频数小于 `param2`，则该圆心无效。
    - 所有圆心半径估计后，按频数优先、半径优先、X 坐标优先、Y 坐标优先排序。
    - 排序后，依次移除距离小于 `minDist` 的重合圆心，保证最终结果中圆心间距足够。
    - 最终只保留前 `maxCircles` 个圆心。

- 若 `centerOnly=True`，则只检测圆心，不估计半径：
    - 仅移除重合圆心，返回时半径设为0。

- 该步骤会得到：
    - `circles`：最终检测到的圆列表，格式为 `[[x, y, r], ...]`，其中 `x`、`y` 为圆心坐标，`r` 为半径。


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