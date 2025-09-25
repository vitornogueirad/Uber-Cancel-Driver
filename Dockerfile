# Imagem base (Linux + Python 3.11)
FROM python:3.12

# Diretório de trabalho dentro do container
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia todo o código e artefatos para dentro da imagem
COPY . .

EXPOSE 8000

# Inicialização
CMD ["gunicorn", "src.driver_cancel.api.service:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "2", "--threads", "2", \
     "--bind", "0.0.0.0:8000", "--timeout", "60", "--log-level", "info"]
