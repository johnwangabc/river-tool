"""
生成巡河宝统计工具的应用图标
主题：水滴 + 统计图表
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """创建应用图标 - 水滴 + 统计主题"""
    # 创建图像
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    import math

    # 背景渐变色 (蓝色系)
    for i in range(size):
        # 从浅蓝到深蓝的渐变
        r = int(100 - (i / size) * 30)
        g = int(180 - (i / size) * 50)
        b = int(230 - (i / size) * 30)
        draw.rectangle([(0, i), (size, i+1)], fill=(r, g, b, 255))

    # 绘制水滴形状
    center_x = size // 2
    center_y = size // 2 - size // 10

    # 水滴参数
    drop_width = size // 2.5
    drop_height = size // 2

    # 绘制水滴路径
    points = []
    import math
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        if angle <= 180:
            # 上半部分 - 圆形
            x = center_x + drop_width * math.cos(rad)
            y = center_y + drop_width * math.sin(rad)
        else:
            # 下半部分 - 尖锐
            x = center_x + drop_width * math.cos(rad) * (1 - (angle - 180) / 180 * 0.7)
            y = center_y + drop_height * math.sin(rad) * 1.2
        points.append((x, y))

    # 绘制白色水滴
    draw.polygon(points, fill=(255, 255, 255, 255))

    # 在水滴内绘制统计图标
    bar_width = size // 20
    bar_spacing = size // 25
    bar_start_x = center_x - bar_width * 1.5 - bar_spacing
    bar_base_y = center_y + size // 8

    # 绘制三个柱状图
    bar_heights = [size // 8, size // 5, size // 6.5]
    colors = [(70, 130, 200), (80, 150, 220), (90, 170, 240)]

    for i, (height, color) in enumerate(zip(bar_heights, colors)):
        x = bar_start_x + i * (bar_width + bar_spacing)
        y = bar_base_y - height
        draw.rectangle(
            [(x, y), (x + bar_width, bar_base_y)],
            fill=color
        )

    # 添加文字 "巡河"
    try:
        # 尝试使用中文字体
        font_size = size // 6
        try:
            font = ImageFont.truetype("msyh.ttc", font_size)  # 微软雅黑
        except:
            try:
                font = ImageFont.truetype("simhei.ttf", font_size)  # 黑体
            except:
                font = ImageFont.truetype("arial.ttf", font_size)  # 备用

        text = "巡河"
        # 获取文字大小
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_x = center_x - text_width // 2
        text_y = center_y + size // 4

        # 绘制文字阴影
        draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 100), font=font)
        # 绘制文字
        draw.text((text_x, text_y), text, fill=(70, 130, 200), font=font)
    except Exception as e:
        print(f"无法添加文字: {e}")

    # 保存图像
    img.save(filename, 'PNG')
    print(f"[OK] 已生成: {filename} ({size}x{size})")


def create_adaptive_icon(size, filename):
    """创建Android自适应图标 - 仅前景"""
    # 创建透明背景
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    import math

    # 绘制水滴形状 (与icon相同但更大，适应安全区域)
    center_x = size // 2
    center_y = size // 2

    # 水滴参数 (稍大一些)
    drop_width = size // 2.2
    drop_height = size // 1.8

    # 绘制水滴路径
    points = []
    for angle in range(0, 360, 5):
        rad = math.radians(angle)
        if angle <= 180:
            x = center_x + drop_width * math.cos(rad)
            y = center_y - size // 15 + drop_width * math.sin(rad)
        else:
            x = center_x + drop_width * math.cos(rad) * (1 - (angle - 180) / 180 * 0.7)
            y = center_y - size // 15 + drop_height * math.sin(rad) * 1.2
        points.append((x, y))

    # 绘制蓝色水滴
    draw.polygon(points, fill=(70, 150, 220, 255))

    # 添加白色高光
    highlight_points = []
    for angle in range(45, 135, 5):
        rad = math.radians(angle)
        x = center_x - size // 8 + (drop_width // 3) * math.cos(rad)
        y = center_y - size // 6 + (drop_width // 3) * math.sin(rad)
        highlight_points.append((x, y))

    if highlight_points:
        draw.polygon(highlight_points, fill=(255, 255, 255, 150))

    # 在水滴内绘制统计图标
    bar_width = size // 18
    bar_spacing = size // 22
    bar_start_x = center_x - bar_width * 1.5 - bar_spacing
    bar_base_y = center_y + size // 6

    # 绘制三个柱状图
    bar_heights = [size // 7, size // 4.5, size // 6]

    for i, height in enumerate(bar_heights):
        x = bar_start_x + i * (bar_width + bar_spacing)
        y = bar_base_y - height
        draw.rectangle(
            [(x, y), (x + bar_width, bar_base_y)],
            fill=(255, 255, 255, 255)
        )

    # 保存图像
    img.save(filename, 'PNG')
    print(f"[OK] 已生成: {filename} ({size}x{size})")


def create_splash(width, height, filename):
    """创建启动画面"""
    # 创建图像
    img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    import math

    # 背景渐变色 (从上到下，白色到浅蓝色)
    for i in range(height):
        progress = i / height
        r = int(255 - progress * 155)
        g = int(255 - progress * 75)
        b = int(255 - progress * 25)
        draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b, 255))

    # 绘制大水滴
    center_x = width // 2
    center_y = height // 2 - height // 8

    drop_width = width // 4
    drop_height = height // 3.5

    # 绘制水滴路径
    points = []
    for angle in range(0, 360, 3):
        rad = math.radians(angle)
        if angle <= 180:
            x = center_x + drop_width * math.cos(rad)
            y = center_y + drop_width * math.sin(rad)
        else:
            x = center_x + drop_width * math.cos(rad) * (1 - (angle - 180) / 180 * 0.7)
            y = center_y + drop_height * math.sin(rad) * 1.2
        points.append((x, y))

    # 绘制水滴阴影
    shadow_points = [(x + 10, y + 10) for x, y in points]
    draw.polygon(shadow_points, fill=(200, 200, 200, 100))

    # 绘制蓝色水滴
    draw.polygon(points, fill=(70, 150, 220, 255))

    # 添加白色高光
    highlight_points = []
    for angle in range(45, 135, 5):
        rad = math.radians(angle)
        x = center_x - width // 12 + (drop_width // 2.5) * math.cos(rad)
        y = center_y - height // 12 + (drop_width // 2.5) * math.sin(rad)
        highlight_points.append((x, y))

    if highlight_points:
        draw.polygon(highlight_points, fill=(255, 255, 255, 180))

    # 添加统计图标
    bar_width = width // 35
    bar_spacing = width // 45
    bar_start_x = center_x - bar_width * 1.5 - bar_spacing
    bar_base_y = center_y + height // 10

    bar_heights = [height // 12, height // 8, height // 10]

    for i, bar_height in enumerate(bar_heights):
        x = bar_start_x + i * (bar_width + bar_spacing)
        y = bar_base_y - bar_height
        draw.rectangle(
            [(x, y), (x + bar_width, bar_base_y)],
            fill=(255, 255, 255, 255)
        )

    # 添加应用标题
    try:
        font_size = width // 15
        try:
            font = ImageFont.truetype("msyh.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("simhei.ttf", font_size)
            except:
                font = ImageFont.truetype("arial.ttf", font_size)

        title = "巡河宝统计工具"
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]

        text_x = center_x - text_width // 2
        text_y = center_y + height // 4

        # 文字阴影
        draw.text((text_x + 3, text_y + 3), title, fill=(0, 0, 0, 80), font=font)
        # 文字
        draw.text((text_x, text_y), title, fill=(50, 120, 200), font=font)

        # 添加副标题
        subtitle_size = font_size // 2
        try:
            subtitle_font = ImageFont.truetype("msyh.ttc", subtitle_size)
        except:
            try:
                subtitle_font = ImageFont.truetype("simhei.ttf", subtitle_size)
            except:
                subtitle_font = ImageFont.truetype("arial.ttf", subtitle_size)

        subtitle = "River Patrol Statistics"
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = bbox[2] - bbox[0]

        subtitle_x = center_x - subtitle_width // 2
        subtitle_y = text_y + font_size + 20

        draw.text((subtitle_x, subtitle_y), subtitle, fill=(100, 150, 200), font=subtitle_font)

    except Exception as e:
        print(f"无法添加文字: {e}")

    # 保存图像
    img.save(filename, 'PNG')
    print(f"[OK] 已生成: {filename} ({width}x{height})")


def create_favicon(size, filename):
    """创建网站图标"""
    # 创建图像
    img = Image.new('RGBA', (size, size), (70, 150, 220, 255))
    draw = ImageDraw.Draw(img)
    import math

    # 绘制简化的水滴
    center_x = size // 2
    center_y = size // 2 - size // 10

    drop_width = size // 3
    drop_height = size // 2.5

    points = []
    import math
    for angle in range(0, 360, 10):
        rad = math.radians(angle)
        if angle <= 180:
            x = center_x + drop_width * math.cos(rad)
            y = center_y + drop_width * math.sin(rad)
        else:
            x = center_x + drop_width * math.cos(rad) * (1 - (angle - 180) / 180 * 0.7)
            y = center_y + drop_height * math.sin(rad) * 1.2
        points.append((x, y))

    draw.polygon(points, fill=(255, 255, 255, 255))

    # 保存图像
    img.save(filename, 'PNG')
    print(f"[OK] 已生成: {filename} ({size}x{size})")


def main():
    """主函数"""
    print("=" * 50)
    print("巡河宝统计工具 - 图标生成器")
    print("=" * 50)
    print()

    # 确保assets目录存在
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"[DIR] 已创建目录: {assets_dir}")

    print("开始生成图标...")
    print()

    # 生成各种尺寸的图标
    create_icon(1024, os.path.join(assets_dir, 'icon.png'))
    create_adaptive_icon(1024, os.path.join(assets_dir, 'adaptive-icon.png'))
    create_splash(1242, 2436, os.path.join(assets_dir, 'splash.png'))
    create_favicon(48, os.path.join(assets_dir, 'favicon.png'))

    print()
    print("=" * 50)
    print("[SUCCESS] 所有图标生成完成！")
    print("=" * 50)
    print()
    print("生成的文件：")
    print(f"  - assets/icon.png (1024x1024) - 应用图标")
    print(f"  - assets/adaptive-icon.png (1024x1024) - Android自适应图标")
    print(f"  - assets/splash.png (1242x2436) - 启动画面")
    print(f"  - assets/favicon.png (48x48) - 网站图标")
    print()
    print("现在可以运行 'npm start' 或 'eas build' 了！")
    print()


if __name__ == "__main__":
    main()
