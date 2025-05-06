import cv2 as cv
import numpy as np

img = cv.imread(r"1.bmp")
if img is None:
    raise FileNotFoundError("图片路径错误或文件损坏")

# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = img[:, :, 1]
gray = cv.medianBlur(gray, 5)
# gray = cv.equalizeHist(gray)          # 增强对比度，常规照片很有用


def detect(gray_img, params):
    """
    执行圆检测计算，输入灰度图像和参数字典，输出圆信息对象。
    """
    circles = cv.HoughCircles(
        gray_img, cv.HOUGH_GRADIENT,
        params["dp"], params["minDist"],
        param1=params["param1"],
        param2=params["param2"],
        minRadius=params["minRadius"],
        maxRadius=params["maxRadius"]
    )
    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
    return circles

def draw_result(image, circles):
    """
    输入原图和圆信息，输出带有圆标记的图片。
    """
    vis = cv.cvtColor(image, cv.COLOR_GRAY2BGR)
    if circles is not None:
        for (x, y, r) in circles:
            cv.circle(vis, (x, y), r, (0, 0, 255), 2)
    return vis

def print_result(circles):
    """
    根据圆信息对象输出命令行信息。
    """
    if circles is not None:
        print(f"找到 {len(circles)} 个圆")
        # for idx, (x, y, r) in enumerate(circles, 1):
            # print(f"  圆{idx}: center=({x},{y}), radius={r}")
    else:
        print("未检测到圆")

def get_current_params():
    return {
        "dp": cv.getTrackbarPos("dp x10", "Hough tune") / 10.0,
        "minDist": cv.getTrackbarPos("minDist", "Hough tune"),
        "param1": cv.getTrackbarPos("param1", "Hough tune"),
        "param2": cv.getTrackbarPos("param2", "Hough tune"),
        "minRadius": cv.getTrackbarPos("minRadius", "Hough tune"),
        "maxRadius": cv.getTrackbarPos("maxRadius", "Hough tune")
    }

def update():
    global params, vis
    params = get_current_params()
    circles = detect(gray, params)
    vis = draw_result(gray, circles)
    print_result(circles)
    cv.imshow("Hough tune", vis)


# === 调参交互窗口 ===
cv.namedWindow("Hough tune", cv.WINDOW_NORMAL)
cv.createTrackbar("dp x10",     "Hough tune", 6, 30, lambda x: update())   # 1.2–3.0
cv.createTrackbar("minDist",    "Hough tune", 5, 200, lambda x: update())
cv.createTrackbar("param1",     "Hough tune", 29, 300, lambda x: update())
cv.createTrackbar("param2",     "Hough tune", 29, 100, lambda x: update())
cv.createTrackbar("minRadius",  "Hough tune", 203, 300, lambda x: update())
cv.createTrackbar("maxRadius",  "Hough tune", 261, 400, lambda x: update())

# === 全局变量 ===
# 存储参数值
params = {
    "dp": 0,
    "minDist": 0,
    "param1": 0,
    "param2": 0,
    "minRadius": 0,
    "maxRadius": 0
}

# 初始化vis图像
vis = img.copy()
cv.imshow("Hough tune", vis)


# 初始调用一次，确保界面有内容
update()

while True:
    key = cv.waitKey(50)
    if key == 27:
        break

cv.destroyAllWindows()
