import cv2 as cv
import numpy as np

img = cv.imread(r"D:\PycharmProjects\pythonProject\pai.bmp")
if img is None:
    raise FileNotFoundError("图片路径错误或文件损坏")

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
gray = cv.medianBlur(gray, 5)
gray = cv.equalizeHist(gray)          # 增强对比度，常规照片很有用

# === 调参交互窗口 ===
def nothing(x): pass
cv.namedWindow("Hough tune", cv.WINDOW_NORMAL)
cv.createTrackbar("dp x10",     "Hough tune", 12, 30, nothing)   # 1.2–3.0
cv.createTrackbar("minDist",    "Hough tune", 20, 200, nothing)
cv.createTrackbar("param1",     "Hough tune", 100, 300, nothing)
cv.createTrackbar("param2",     "Hough tune", 25, 100, nothing)
cv.createTrackbar("minRadius",  "Hough tune", 30, 300, nothing)
cv.createTrackbar("maxRadius",  "Hough tune", 150, 400, nothing)

while True:
    dp        = cv.getTrackbarPos("dp x10",  "Hough tune") / 10.0
    minDist   = cv.getTrackbarPos("minDist", "Hough tune")
    p1        = cv.getTrackbarPos("param1",  "Hough tune")
    p2        = cv.getTrackbarPos("param2",  "Hough tune")
    minR      = cv.getTrackbarPos("minRadius","Hough tune")
    maxR      = cv.getTrackbarPos("maxRadius","Hough tune")
    maxR      = 0 if maxR == 0 else maxR     # 0 表示不设上限

    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, dp, minDist,
                              param1=p1, param2=p2,
                              minRadius=minR, maxRadius=maxR)

    vis = img.copy()
    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        for (x, y, r) in circles:
            cv.circle(vis, (x, y), r, (0, 0, 255), 2)
        print(f"找到 {len(circles)} 个圆")
    else:
        print("未检测到圆")

    cv.imshow("Hough tune", vis)
    if cv.waitKey(30) == 27:  # 按 ESC 退出
        break
cv.destroyAllWindows()
