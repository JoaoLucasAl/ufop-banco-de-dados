# Usa uma imagem base do Python
FROM python:3.9-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o arquivo de dependências para a imagem
COPY requirements.txt /app/

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos da pasta atual (host) para /app (container)
COPY . /app

# Expoe a porta usada pelo Streamlit
EXPOSE 8501

# Define o comando padrão para rodar sua aplicação
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
