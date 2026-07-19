FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# A porta é injetada dinamicamente pela plataforma de deploy (Render define
# $PORT em tempo de execução); 7860 é usado como fallback para rodar o
# container localmente sem variável de ambiente definida.
EXPOSE 7860

CMD ["sh", "-c", "chainlit run app.py --host 0.0.0.0 --port ${PORT:-7860} --headless"]
