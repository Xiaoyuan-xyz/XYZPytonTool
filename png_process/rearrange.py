# 在一个目录下 将所有以png结尾的图片作如下处理 每张图片都是128宽512高，分为若干16*16的方格，每行8个，现在重新排列，每行16个，将他们变成256*256的图片


import os
from PIL import Image

input_dir = r"H:\Resource\演舞解包\gn_dat5.arc\map\chip"
output_dir = r"H:\Resource\演舞解包\tileset"

os.makedirs(output_dir, exist_ok=True)

TILE_SIZE = 16
OLD_COLS = 8
NEW_COLS = 16

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(".png"):
        continue

    path = os.path.join(input_dir, filename)
    img = Image.open(path)

    width, height = img.size
    cols = width // TILE_SIZE
    rows = height // TILE_SIZE

    tiles = []

    # 读取所有 tile
    for y in range(rows):
        for x in range(cols):
            tile = img.crop((
                x * TILE_SIZE,
                y * TILE_SIZE,
                (x + 1) * TILE_SIZE,
                (y + 1) * TILE_SIZE
            ))
            tiles.append(tile)

    total_tiles = len(tiles)
    new_rows = total_tiles // NEW_COLS

    new_img = Image.new("RGBA", (NEW_COLS * TILE_SIZE, new_rows * TILE_SIZE))

    # 重新排列
    for i, tile in enumerate(tiles):
        nx = i % NEW_COLS
        ny = i // NEW_COLS

        new_img.paste(tile, (nx * TILE_SIZE, ny * TILE_SIZE))

    save_path = os.path.join(output_dir, filename)
    new_img.save(save_path)

    print(f"processed: {filename}")