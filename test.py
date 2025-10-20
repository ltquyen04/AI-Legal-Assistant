import pandas as pd

# Đường dẫn file CSV
csv_path = "qa.csv"

# Danh sách văn bản pháp luật cần giữ lại
valid_documents = [
    "Luật Cư trú 2020",
    "Nghị định 144/2021",
    "Nghị định 154/2024",
    "Nghị định 62/2021",
    "Thông tư 55/2021",
    "Thông tư 56/2021"
]

# Đọc file CSV
df = pd.read_csv(csv_path)

# Hàm kiểm tra xem trường law_article có chứa văn bản hợp lệ không
def is_valid_law(law_article):
    if pd.isna(law_article):
        return False
    return any(doc in law_article for doc in valid_documents)

# Lọc các dòng hợp lệ
filtered_df = df[df["law_article"].apply(is_valid_law)]

# Xuất lại file CSV (ghi đè)
filtered_df.to_csv(csv_path, index=False)

print(f"✅ Đã lọc xong: giữ lại {len(filtered_df)} dòng hợp lệ trong '{csv_path}'.")
