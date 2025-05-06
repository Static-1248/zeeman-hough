import cv2
import numpy as np

def main():
    # 创建一个简单的黑色图像
    image = np.zeros((500, 500, 3), dtype="uint8")

    # 在图像上绘制一个白色圆环
    center_coordinates = (250, 250)  # 圆心坐标
    radius = 100  # 半径
    color = (255, 255, 255)  # 白色
    thickness = 2  # 圆环线条粗细
    cv2.circle(image, center_coordinates, radius, color, thickness)

    # 显示图像
    cv2.imshow("Test Image", image)

    # 等待按键输入后关闭窗口
    print("Press any key in the image window to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()