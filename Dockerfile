FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m nltk.downloader vader_lexicon
COPY . .
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "ui/App_v3_Final.py", "--server.port=8501", "--server.address=0.0.0.0"]
