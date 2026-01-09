from PIL import Image, ImageDraw, ImageFilter

# 图片尺寸
width, height = 1920, 1080

# 创建透明背景的图片
image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

# 创建一个绘图对象
draw = ImageDraw.Draw(image)

# 圆的半径
radius = min(width, height) // 4

# 圆心坐标
center = (width // 2, height // 2)

# 画一个纯白圆，但比目标半径稍大一些，用于模糊过渡
blur_radius = 50  # 模糊范围，可调
draw.ellipse(
    [
        (center[0] - radius - blur_radius, center[1] - radius - blur_radius),
        (center[0] + radius + blur_radius, center[1] + radius + blur_radius)
    ],
    fill=(255, 255, 255, 255)
)

# 应用高斯模糊
image = image.filter(ImageFilter.GaussianBlur(radius=blur_radius))

# 保存图片
image.save("white_circle_blur.png")
