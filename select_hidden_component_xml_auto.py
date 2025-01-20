import os
import shutil

# 原始文件夹所在的根目录路径，你可以根据实际情况调整
root_folder = r"D:\code\must\15apk\apk"
# 目标文件夹路径
destination_folder = r"D:\code\must\15apk\spinner_xml_files"

def checkIfHasLayout(file_name, root, files):
    # 用于统计包含spinner控件的文件个数
    spinner_count = 0
    # 用于统计包含expandablelistview控件的文件个数
    expandablelistview_count = 0
    # 用于存储包含expandablelistview控件的文件名
    expandablelistview_file_names = []
    print("-----------------------------------")
    print(f"当前文件夹: {root}")

    for file in files:
        if file.endswith(".xml"):
            file_path = os.path.join(root, file)
            # 读取xml文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 判断文件内容是否包含spinner
                if 'Spinner' in content:
                    spinner_count += 1
                # 判断文件内容是否包含expandablelistview
                if 'ExpandableListView' in content:
                    expandablelistview_count += 1
                    expandablelistview_file_names.append(file)
                # 判断文件内容是否包含spinner或者expandablelistview
                if 'Spinner' in content or 'ExpandableListView' in content:

                    # 将文件复制到目标文件夹
                    destination_file_folder = os.path.join(destination_folder, file_name)
                    # 如果目标文件夹不存在，则创建
                    if not os.path.exists(destination_file_folder):
                        os.makedirs(destination_file_folder)

                    destination_path = os.path.join(destination_file_folder, file)
                    shutil.copyfile(file_path, destination_path)
                    print(f"已复制文件: {file_path} 到 {destination_path}")




    print(f"包含spinner控件的文件个数为: {spinner_count}")
    print(f"包含expandablelistview控件的文件个数为: {expandablelistview_count}")
    print("包含expandablelistview控件的文件名如下:")
    for name in expandablelistview_file_names:
        print(name)
    print("筛选完成。")


def findTargetInPath(file_name):
    base_path = os.path.join(root_folder, file_name)

    for apk_dir in os.listdir(base_path):
        if '.' not in apk_dir or apk_dir.startswith("."):
            continue
        if apk_dir.endswith(".apk") or os.path.isdir(os.path.join(base_path, apk_dir)) is False:
            continue

        apk_folder = os.listdir(os.path.join(base_path, apk_dir, "res"))
        for folder in apk_folder:
            if 'layout' == folder:
                for root, _, files in os.walk(os.path.join(base_path, apk_dir, "res", folder)):
                    checkIfHasLayout(file_name, root, files)


if __name__ == '__main__':
    file_names = os.listdir(root_folder)
    # 遍历根目录下所有子文件夹
    for file_name in file_names:
        findTargetInPath(file_name)



