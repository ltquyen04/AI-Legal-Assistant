import pandas as pd
import re
from tqdm import tqdm

# Load dữ liệu
qa_df = pd.read_csv("data/qa.csv")
legal_df = pd.read_csv("data/legal_data.csv")

# Bảng ánh xạ tên văn bản -> mã
law_map = {
    "Luật Cư trú 2020": "68/2020/QH14",
    "Nghị định 154/2024": "154/2024/NĐ-CP",
    "Nghị định 144/2021": "144/2021/NĐ-CP",
    "Nghị định 62/2021": "62/2021/NĐ-CP",
    "Thông tư 55/2021": "55/2021/TT-BCA",
    "Thông tư 56/2021": "56/2021/TT-BCA"
}

# Hàm chuẩn hóa law_article -> danh sách law_id tương ứng
def extract_law_ids(law_article_text):
    if pd.isna(law_article_text):
        return []

    result = []
    # Tách theo ; hoặc newline
    entries = re.split(r'[;\n]', law_article_text)

    for entry in entries:
        entry = entry.strip()
        # Tìm "Điều X ..." trong entry
        match = re.search(r"Điều\s+(\d+)", entry)
        if not match:
            continue
        dieu = match.group(1)
        for name, code in law_map.items():
            if name in entry:
                law_id = f"{code}_{dieu}"
                result.append(law_id)
                break
        else:
            # Nếu không chứa văn bản cụ thể, kiểm tra nếu chỉ là "Điều X Luật/Nghị định..."
            for name, code in law_map.items():
                if name.split()[0] in entry:  # khớp "Luật", "Nghị định", "Thông tư"
                    law_id = f"{code}_{dieu}"
                    result.append(law_id)
                    break
    return result

# Tạo nhãn
rows = []

for _, row in tqdm(qa_df.iterrows(), total=len(qa_df)):
    question = row["question"]
    article_field = row["law_article"]
    positive_ids = extract_law_ids(article_field)

    for law_id in legal_df["id"]:
        label = 1 if law_id in positive_ids else 0
        rows.append({
            "question": question,
            "law_id": law_id,
            "label": label
        })

# Tạo DataFrame và lưu
qa_label_df = pd.DataFrame(rows)
qa_label_df.to_csv("data/qa_label.csv", index=False)
