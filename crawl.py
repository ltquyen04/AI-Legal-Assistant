import os
import re
from docx import Document

FOLDER_PATH = "data_legal"

# Chuỗi các ký tự tiếng Việt có dấu phổ biến trong đề mục
VIETNAM_CHAR = "a-zA-Z0-9đĐăĂâÂêÊôÔơƠưƯáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ"

def clean_line(line):
    pattern = rf'(^|[\s“"(\[])([{VIETNAM_CHAR}]{{1,5}}[\.\:\)\-])\s+'
    line = re.sub(pattern, r'\1', line)
    # Xoá các ký hiệu đầu dòng phổ biến như –, -, *, • nếu có
    line = re.sub(r'^[\-\–\—\•\*]+\s*', '', line)
    return line.strip()

def extract_law_contents_lines_from_docx(file_path):
    doc = Document(file_path)
    law_lines = []
    inside_law = False

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        if re.match(r'^Điều\s+\d+[A-Z]*\.?', text):
            inside_law = True
            continue

        if inside_law:
            law_lines.append(text)

    return law_lines

def crawl_all_documents(folder_path):
    all_lines = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx"):
            file_path = os.path.join(folder_path, filename)
            print(f"📄 Đang xử lý: {filename}")
            law_lines = extract_law_contents_lines_from_docx(file_path)
            cleaned = [clean_line(line) for line in law_lines if clean_line(line)]
            all_lines.extend(cleaned)

            # Thêm 1 dòng trắng để ngắt giữa các văn bản khác nhau
            all_lines.append("")

    # Loại bỏ các dòng trùng lặp nhưng giữ thứ tự xuất hiện
    unique_lines = list(dict.fromkeys(all_lines))
    return unique_lines

def save_to_file(lines, out_path="legal_text.txt"):
    with open(out_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

if __name__ == "__main__":
    lines = crawl_all_documents(FOLDER_PATH)
    save_to_file(lines)
    print(f"✅ Đã trích xuất {len(lines)} dòng vào legal-text.txt")
