FROM python:3.12.16-slim
WORKDIR /avi_server
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "fake_server.py"]