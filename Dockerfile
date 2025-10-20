FROM python:3.11

# Cài thư viện hệ thống (underthesea yêu cầu)
RUN apt-get update && apt-get install -y build-essential curl git && rm -rf /var/lib/apt/lists/*

# Cài thư viện Python
RUN pip install --upgrade pip maturin underthesea python-docx tqdm 

# Cài đặt các thư viện bổ sung
RUN pip install requests beautifulsoup4

# Thư mục làm việc
WORKDIR /app

# Copy mã nguồn
COPY . /app
