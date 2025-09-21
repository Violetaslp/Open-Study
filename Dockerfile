FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY bot.py .

RUN pip install --no-cache-dir -r requirements.txt

# Токен Telegram передаётся через Secret Render
ENV TOKEN=your_telegram_bot_token_here

CMD ["python", "bot.py"]
