FROM pypy:3.10-slim-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

ENV TZ=Asia/Bangkok

CMD ["sh", "/app/always_run.sh"]
