import os

from PIL import Image
from tqdm import tqdm


def make_transparent(input_path, output_path):
    img = Image.open(input_path)
    if img.format != 'PNG':
        print(f'错误的文件名：{input_path}')
        return

    transparent_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
    transparent_img.save(output_path, format='PNG')


path = input('请输入待处理的文件夹：')
files = os.listdir(path)
image_dirs = [file for file in files if file.lower().endswith('.png')]
for image_dir in tqdm(image_dirs):
    image_path = os.path.join(path, image_dir)
    make_transparent(image_path, image_path)
