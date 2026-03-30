FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install pyTelegramBotAPI flask requests
CMD ["python", "app.py"]
