FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
COPY bot.py .
COPY credentials.json .
RUN pip install --no-cache-dir -r requirements.txt
ENV TOKEN=your_telegram_bot_token_here
CMD ["python", "bot.py"]
