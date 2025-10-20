import requests
from bs4 import BeautifulSoup
import csv
import os
import hashlib
import re
from urllib.parse import urljoin
from tqdm import tqdm

# Cấu hình
KEYWORDS = ["tạm vắng", "tạm trú", "thường trú", "cư trú", "lưu trú"]
CSV_PATH = "qa.csv"
BASE_URL = "https://thuvienphapluat.vn"
SEARCH_URL = BASE_URL + "/phap-luat/tim-tu-van?searchType={}&q={}&searchField=0&page={}"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 40

def check_site_accessible(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def extract_detail_multi_qa(detail_url):
    try:
        res = requests.get(detail_url, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        section = soup.find("section")
        if not section:
            return []

        h2_tags = section.find_all("h2")
        qa_list = []

        tags = [a.get_text(strip=True) for a in soup.find_all("a", class_="kwseo")]
        tag_text = ", ".join(tags)

        for h2 in h2_tags:
            question = h2.get_text(strip=True)
            answer_parts = []
            law_articles = set()

            current = h2.find_next_sibling()
            while current:
                if current.name == "h2":
                    break
                if current.name == "p":
                    answer_parts.append(current.get_text(" ", strip=True))
                    for a in current.find_all("a", href=True):
                        if "/van-ban/" in a["href"]:
                            raw_text = a.get_text(" ", strip=True)

                            # Trích xuất Điều
                            dieu_matches = re.findall(r"Điều\s+\d+[a-zA-Z]*", raw_text, re.IGNORECASE)

                            # Trích xuất văn bản: Luật / Nghị định / Thông tư
                            law_matches = re.findall(r"(?:Luật|Nghị định|Thông tư)[^.;:\n]*", raw_text, re.IGNORECASE)

                            for d in dieu_matches:
                                for l in law_matches or [""]:
                                    law_articles.add(f"{d} {l}".strip())

                            if not dieu_matches and law_matches:
                                law_articles.update(law_matches)

                current = current.find_next_sibling()

            answer = "\n".join(answer_parts)
            if question and answer:
                qa_list.append({
                    "question": question,
                    "answer": answer,
                    "tag": tag_text,
                    "law_article": "; ".join(sorted(law_articles))
                })

        return qa_list
    except Exception as e:
        print(f"❌ Lỗi khi tải chi tiết: {e}")
        return []


def main():
    if not check_site_accessible(BASE_URL):
        print("⛔ Không thể truy cập trang web thuvienphapluat.vn")
        return

    existing_hashes = set()
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row['question'] + row['answer']
                existing_hashes.add(hashlib.md5(key.encode('utf-8')).hexdigest())

    new_rows = []
    for keyword in tqdm(KEYWORDS, desc="🔍 Từ khoá"):
        for page in tqdm(range(1, MAX_PAGES + 1), desc=f"  📄 Trang", leave=False):
            for search_type in [0, 1]:
                search_link = SEARCH_URL.format(search_type, keyword, page)
                try:
                    res = requests.get(search_link, headers=HEADERS)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    articles = soup.select("article.news-card.tvpl-find")
                    for article in tqdm(articles, desc="    📌 Trang chi tiết", leave=False):
                        a = article.find('a', href=True)
                        if a:
                            full_url = urljoin(BASE_URL, a["href"])
                            qa_list = extract_detail_multi_qa(full_url)
                            for qa in qa_list:
                                key = qa["question"] + qa["answer"]
                                key_hash = hashlib.md5(key.encode("utf-8")).hexdigest()
                                if key_hash not in existing_hashes:
                                    existing_hashes.add(key_hash)
                                    new_rows.append(qa)
                except Exception as e:
                    print(f"⚠️ Lỗi khi tải trang tìm kiếm: {e}")

    unique_questions = set()
    filtered_rows = []
    for row in new_rows:
        q = row["question"].strip()
        if q not in unique_questions:
            unique_questions.add(q)
            filtered_rows.append(row)

    if filtered_rows:
        file_exists = os.path.exists(CSV_PATH)
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["question", "answer", "tag", "law_article"],
                quoting=csv.QUOTE_ALL
            )
            if not file_exists:
                writer.writeheader()
            writer.writerows(filtered_rows)

        print(f"✅ Đã thêm {len(filtered_rows)} câu hỏi mới vào {CSV_PATH}")
    else:
        print("ℹ️ Không có câu hỏi mới nào được thêm.")

if __name__ == "__main__":
    main()
