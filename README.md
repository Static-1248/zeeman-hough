# 塞曼效应光谱环检测程序

这些都是Claude写的 Claude牛逼

---

这个程序用于在塞曼效应的观测实验中，使用OpenCV的HoughCircles算法对拍摄的光谱环照片进行分析，准确测定圆环的位置和大小，从而提高相关物理量的计算精度。

## 功能特点

- 使用OpenCV的HoughCircles算法检测BMP格式图像中的圆环
- 支持单张图像处理和批量处理
- 可视化显示检测结果，包括原始图像、边缘检测和圆环标记
- 自动保存处理结果
- 提供测试模式，生成测试图像进行算法验证

## 安装依赖

程序依赖以下Python库：

```bash
conda activate phylab25xd  # 激活已配置的conda环境
conda install -c conda-forge opencv
conda install jupyter notebook
conda install numpy matplotlib
```

Jupyter Lab 安装：

```bash
conda install -c conda-forge jupyterlab jupyter-collaboration ipywidgets
```

## 使用方法

### 基本用法

```bash
python zeeman_circle_detector.py [图像路径或目录路径]
```

- 如果提供图像文件路径，程序将处理单个图像
- 如果提供目录路径，程序将处理目录中所有BMP格式图像
- 如果不提供参数，程序将创建一个测试图像并进行检测

### 示例

```bash
# 处理单个图像
python zeeman_circle_detector.py sample.bmp

# 处理目录中所有BMP图像
python zeeman_circle_detector.py ./images/

# 测试模式
python zeeman_circle_detector.py
```

## 参数调整

如果检测效果不理想，可以在`zeeman_circle_detector.py`文件中调整HoughCircles算法的参数：

```python
circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1,              # 累加器分辨率与图像分辨率的比率
    minDist=50,        # 检测到的圆之间的最小距离
    param1=50,         # Canny边缘检测的高阈值
    param2=30,         # 累加器阈值，越小检测到的圆越多
    minRadius=10,      # 最小圆半径
    maxRadius=300      # 最大圆半径
)
```

### 参数说明

- `dp`：累加器分辨率与图像分辨率的比率，通常设为1
- `minDist`：检测到的圆之间的最小距离，根据图像中圆环的密集程度调整
- `param1`：Canny边缘检测的高阈值，影响边缘检测的灵敏度
- `param2`：累加器阈值，值越小检测到的圆越多（可能包含更多误检），值越大检测越严格
- `minRadius`和`maxRadius`：限制检测圆的半径范围，根据实际光谱环的大小调整

## 结果解释

程序运行后会显示：

1. 原始图像
2. 边缘检测结果
3. 圆环检测结果（标记圆心和圆周，并标注圆心坐标和半径）

检测结果将保存在原图像所在目录的`results`子目录中。

## 注意事项

- 图像质量对检测效果有很大影响，建议使用清晰、对比度适中的图像
- 如果检测不到圆环或检测结果不准确，可以尝试调整HoughCircles算法的参数
- 对于复杂背景的图像，可能需要增加预处理步骤，如调整对比度、应用阈值分割等