import numpy as np
from PIL import Image

# 图像大小
width, height = 1920, 1080

# 定义渐变段
segments = [
    (0.70, 0.50, 0.0, 0.85),
    (0.70, 0.90, 0.0, 0.85),
    (0.325, 0.15, 0.2, 0.9),
    (0.325, 0.50, 0.2, 0.9),
    (1.075, 0.90, 0.4, 0.95),
    (1.075, 1.25, 0.4, 0.95),
    (-0.10, 0.15, 0.6, 1.0),
    (-0.10, -0.35, 0.6, 1.0),
]

def ease_out(t):
    if t < 0:
        return 0
    elif t > 1:
        return 1
    return abs(t) ** 6

def get_value(px):
    """给定横向百分比位置 (px)，返回灰度值 [0,255]"""
    for x1, x2, t0, t1 in segments:
        # 判断 px 是否在区间内
        if (x1 >= px >= x2) or (x1 <= px <= x2):
            # 归一化进度
            p = abs(px - x1) / abs(x2 - x1)
            val = ease_out(p) * (t1 - t0) + t0
            return int(val * 255)
    return 0  # 不在任何区间 → 白色

# 创建图像数组
img = np.zeros((height, width), dtype=np.uint8)

for y in range(height):
    # 当前行的水平偏移 (像素数)
    shift = int((0.2 * y / height) * width)
    for x in range(width):
        # 转换到“第一行”的百分比坐标
        px = (x + shift) / width
        gray = get_value(px)
        img[y, x] = 255-gray

# 保存图片
Image.fromarray(img).save("wipe_line.png")
