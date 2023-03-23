FROM python:3.8.10
RUN apt-get update
RUN apt-get install -y tesseract-ocr
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /app
EXPOSE 3000
CMD ["uvicorn", "router:app", "--host", "0.0.0.0", "--port", "3000"]