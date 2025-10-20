import csv

# Khởi tạo file qa.csv chỉ có header
with open('qa.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["question", "answer", "tag", "law_article"])

print("✅ Đã tạo file 'qa.csv' với các trường: question, answer, tag, law_article.")
