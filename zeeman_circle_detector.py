import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
from pathlib import Path

def detect_circles(image_path, show_result=True, save_result=False):
    """
    使用HoughCircles算法检测图像中的圆环
    
    参数:
        image_path: 图像文件路径
        show_result: 是否显示结果
        save_result: 是否保存结果图像
        
    返回:
        circles: 检测到的圆的参数 [x, y, r]
        processed_image: 处理后的图像
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"错误：无法读取图像 {image_path}")
        return None, None
    
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 应用高斯模糊减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 使用Canny边缘检测
    edges = cv2.Canny(blurred, 50, 150)
    
    # 复制原始图像用于显示结果
    output = image.copy()
    
    # 使用HoughCircles检测圆
    # 参数说明:
    # cv2.HOUGH_GRADIENT: 检测方法
    # dp=1: 累加器分辨率与图像分辨率的比率
    # minDist=50: 检测到的圆之间的最小距离
    # param1=50: Canny边缘检测的高阈值
    # param2=30: 累加器阈值，越小检测到的圆越多
    # minRadius=10: 最小圆半径
    # maxRadius=300: 最大圆半径
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=50,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=300
    )
    
    # 检查是否检测到圆
    if circles is not None:
        # 将圆的参数转换为整数
        circles = np.uint16(np.around(circles))
        
        # 在图像上绘制检测到的圆
        for i in circles[0, :]:
            # 绘制圆心
            cv2.circle(output, (i[0], i[1]), 2, (0, 255, 0), 3)
            # 绘制圆周
            cv2.circle(output, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # 在图像上标注圆的参数
            cv2.putText(output, f"({i[0]},{i[1]}),r={i[2]}", 
                       (i[0]-i[2], i[1]-i[2]-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        print(f"检测到 {len(circles[0])} 个圆环")
        for i, circle in enumerate(circles[0]):
            print(f"圆环 {i+1}: 中心=({circle[0]}, {circle[1]}), 半径={circle[2]}")
    else:
        print("未检测到圆环")
    
    # 显示结果
    if show_result and circles is not None:
        # 创建一个图像网格用于显示
        plt.figure(figsize=(15, 5))
        
        # 显示原始图像
        plt.subplot(131)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.title('原始图像')
        plt.axis('off')
        
        # 显示边缘检测结果
        plt.subplot(132)
        plt.imshow(edges, cmap='gray')
        plt.title('边缘检测')
        plt.axis('off')
        
        # 显示圆检测结果
        plt.subplot(133)
        plt.imshow(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
        plt.title('圆环检测结果')
        plt.axis('off')
        
        plt.tight_layout()
        plt.show()
    
    # 保存结果图像
    if save_result and circles is not None:
        output_dir = Path(os.path.dirname(image_path)) / 'results'
        output_dir.mkdir(exist_ok=True)
        
        filename = Path(image_path).stem
        output_path = output_dir / f"{filename}_detected.jpg"
        cv2.imwrite(str(output_path), output)
        print(f"结果已保存至: {output_path}")
    
    return circles, output

def batch_process(directory, pattern="*.bmp"):
    """
    批量处理目录中的所有BMP图像
    
    参数:
        directory: 图像目录
        pattern: 文件匹配模式
    """
    directory = Path(directory)
    image_files = list(directory.glob(pattern))
    
    if not image_files:
        print(f"在 {directory} 中未找到 {pattern} 文件")
        return
    
    print(f"找到 {len(image_files)} 个图像文件")
    
    for image_file in image_files:
        print(f"\n处理图像: {image_file}")
        detect_circles(str(image_file), show_result=True, save_result=True)

def main():
    # 检查命令行参数
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了参数，则处理指定的图像文件
        image_path = sys.argv[1]
        if os.path.isdir(image_path):
            # 如果是目录，则批量处理
            batch_process(image_path)
        elif os.path.isfile(image_path):
            # 如果是文件，则处理单个图像
            detect_circles(image_path, show_result=True, save_result=True)
        else:
            print(f"错误：{image_path} 不是有效的文件或目录")
    else:
        # 如果没有提供参数，则提示用户输入图像路径
        print("请提供BMP图像文件路径或包含BMP图像的目录路径")
        print("用法: python zeeman_circle_detector.py [图像路径或目录路径]")
        
        # 测试模式：创建并检测一个带有圆环的测试图像
        print("\n创建测试图像...")
        test_image = np.zeros((500, 500, 3), dtype="uint8")
        
        # 添加多个同心圆环
        center = (250, 250)
        for radius in [50, 100, 150, 200]:
            cv2.circle(test_image, center, radius, (255, 255, 255), 2)
        
        # 保存测试图像
        test_image_path = "test_circles.bmp"
        cv2.imwrite(test_image_path, test_image)
        print(f"测试图像已保存为: {test_image_path}")
        
        # 检测测试图像中的圆环
        print("\n检测测试图像中的圆环...")
        detect_circles(test_image_path, show_result=True, save_result=True)

if __name__ == "__main__":
    main()