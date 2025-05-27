import os
import re
import shutil
from typing import List, Tuple

def split_medical_cases(input_filepath: str, output_dir: str) -> None:
    """
    读取中医病案文本文件，提取病名和各个病例，将内容追加写入对应文件。
    相同编号的病例会追加到同一个文件中。

    Args:
        input_filepath: 输入文件路径
        output_dir: 输出目录根路径
    """
    if not os.path.isfile(input_filepath):
        raise FileNotFoundError(f"输入文件未找到: {input_filepath}")

    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError as e:
        raise IOError(f"读取文件时出错 {input_filepath}: {e}")

    disease_pattern = r"^\s*[（\(](?:[一二三四五六七八九十]+|[0-9]+)[）\)]([\u4e00-\u9fa5]+(?:[（\(][\u4e00-\u9fa5]+[）\)])?)\s*$"
    disease_match = re.search(disease_pattern, content, re.MULTILINE)
    if not disease_match:
        raise ValueError(f"在文件 {input_filepath} 中未找到符合格式的病名行")
    
    disease_name = disease_match.group(1)
    disease_output_dir = os.path.join(output_dir, disease_name)
    os.makedirs(disease_output_dir, exist_ok=True)

    section_pattern = r"^(例[一二三四五六七八九十]+)"
    markers: List[Tuple[int, str]] = []
    for match in re.finditer(section_pattern, content, re.MULTILINE):
        markers.append((match.start(), match.group(1)))

    if not markers:
        raise ValueError(f"在文件 {input_filepath} 中未找到病例标记")

    num_markers = len(markers)
    for i in range(num_markers):
        start_index = markers[i][0]
        marker_text = markers[i][1]
        end_index = markers[i+1][0] if i + 1 < num_markers else len(content)
        section_content = content[start_index:end_index].strip()
        output_filename = os.path.join(disease_output_dir, f"{marker_text}.txt")

        try:
            with open(output_filename, 'a', encoding='utf-8') as f_out:
                if f_out.tell() == 0:
                    f_out.write(f"病名: {disease_name}\n\n")
                f_out.write(f"{section_content}\n\n")
        except IOError as e:
            raise IOError(f"写入文件时出错 {output_filename}: {e}")

if __name__ == '__main__':
    input_dir = 'input_data'
    output_dir = 'output_data'
    
    if not os.path.isdir(input_dir):
        print(f"错误: 输入目录不存在")
        exit(1)
    
    # 清理整个输出目录
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
        
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_filepath = os.path.join(input_dir, filename)
            print(f"处理文件: {input_filepath}")
            try:
                split_medical_cases(input_filepath, output_dir)
            except Exception as e:
                print(f"处理失败: {str(e)}") 