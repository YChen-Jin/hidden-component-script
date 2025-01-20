import os
import xml.etree.ElementTree as ET
import openpyxl

"""
从根据界面UI分析的xml文件中，计算隐藏控件的上下左右占比
"""

def get_screen_dimensions(root):
    """
    从根节点的第一个包含 bounds 属性的节点获取屏幕宽度和高度
    """
    for node in root.iter():
        bounds = node.attrib.get('bounds')
        if bounds:
            bounds = bounds.strip('[]').split('][')
            (x1, y1) = map(int, bounds[0].split(','))
            (x2, y2) = map(int, bounds[1].split(','))
            width = x2 - x1
            height = y2 - y1
            return width, height
    raise ValueError("Screen dimensions could not be determined from the XML file.")


def calculate_ratios_for_file(xml_file_path, resource_id):
    """
    计算单个 XML 文件中指定 resource-id 控件的上下左右占比
    """
    try:
        # 解析 XML 文件
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # 获取屏幕宽度和高度
        screen_width, screen_height = get_screen_dimensions(root)

        # 遍历 XML 查找指定控件
        for node in root.iter():
            if node.attrib.get('resource-id') == resource_id:
                bounds = node.attrib.get('bounds')
                bounds = bounds.strip('[]').split('][')
                (x1, y1) = map(int, bounds[0].split(','))
                (x2, y2) = map(int, bounds[1].split(','))

                # 计算上下左右的占比
                top_ratio = y1 / screen_height
                bottom_ratio = (screen_height - y2) / screen_height
                left_ratio = x1 / screen_width
                right_ratio = (screen_width - x2) / screen_width

                return {
                    "file_name": os.path.basename(xml_file_path),
                    "resource_id": resource_id,
                    "top_ratio": round(top_ratio, 4),
                    "bottom_ratio": round(bottom_ratio, 4),
                    "left_ratio": round(left_ratio, 4),
                    "right_ratio": round(right_ratio, 4),
                }

        print(f"Warning: Resource ID '{resource_id}' not found in {xml_file_path}.")
        return None

    except Exception as e:
        print(f"Error processing file {xml_file_path}: {e}")
        return None


def process_all_files_to_excel(input_folder, resource_id_map, output_excel_path):
    """
    批量处理文件夹中的所有 XML 文件，并将结果输出到一个 Excel 文件
    """
    # 初始化 Excel 工作簿
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Ratios"

    # 写入标题
    sheet.append(["File Name", "Resource ID", "Top Ratio", "Bottom Ratio", "Left Ratio", "Right Ratio"])

    # 遍历文件夹中的所有 XML 文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".xml"):
            xml_file_path = os.path.join(input_folder, file_name)
            resource_id = resource_id_map.get(file_name, None)

            if resource_id:
                result = calculate_ratios_for_file(xml_file_path, resource_id)

                if result:
                    # 写入结果到 Excel
                    sheet.append([result["file_name"], result["resource_id"], result["top_ratio"],
                                  result["bottom_ratio"], result["left_ratio"], result["right_ratio"]])
            else:
                print(f"Skipping {file_name}: No resource ID specified.")

    # 保存 Excel 文件
    workbook.save(output_excel_path)
    print(f"Results saved to {output_excel_path}")


if __name__ == "__main__":
    # 输入文件夹路径
    input_folder = "D:/code/must/15apk/UIhierarchyFile/com.flauschcode.broccoli/"
    # 输出 Excel 文件路径
    output_excel_path = "D:/code/must/15apk/UIhierarchyFile/com.flauschcode.broccoli/ratios_summary.xlsx"

    # 每个 XML 文件对应的 resource-id 字典
    resource_id_map = {
        "step1_initial_hierarchy.xml": "com.flauschcode.broccoli:id/spinner",
        "step2_after_click_drawer_hierarchy.xml": "com.flauschcode.broccoli:id/design_menu_item_text",
        # 添加其他文件名和对应的 resource-id
    }

    # 批量处理并输出结果到一个 Excel 文件
    process_all_files_to_excel(input_folder, resource_id_map, output_excel_path)
