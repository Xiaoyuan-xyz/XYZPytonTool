# 检查一个目录下的json文件，然后用正则表达式多行匹配
# "elements": \[[\s\S]+\]
# 并将它替换成
# "elements": [\n    ]
# 再保存到源文件中
# 入股如果没有匹配到则删除该文件

import os
import re


def replace_elements_in_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()

    # Use regular expression to find and replace the "elements" section
    pattern = r'"elements": \[[\s\S]+\]'
    replacement = r'"elements": [\n    ]'
    modified_content, count = re.subn(pattern, replacement, content)

    with open(file_path, "w") as file:
        file.write(modified_content)

    if count > 0:
        print(f"Modified {file_path} and saved changes. Found {count} match(es).")
    else:
        os.remove(file_path)
        print(f"No matches found in {file_path}. File deleted.")


def main(directory_path):
    # Get a list of all files in the specified directory
    files = os.listdir(directory_path)

    # Filter out only the JSON files
    json_files = [file for file in files if file.lower().endswith(".json")]

    # Process each JSON file
    for json_file in json_files:
        file_path = os.path.join(directory_path, json_file)
        replace_elements_in_file(file_path)


if __name__ == "__main__":
    target_directory = input('请输入待处理的文件夹：')
    main(target_directory)
