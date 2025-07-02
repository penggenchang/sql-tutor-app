FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt

COPY models/Phi-3-Mini-4K-Instruct_Q6_K.gguf /app/models/

EXPOSE 7860

CMD ["python", "app.py"]
