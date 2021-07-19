FROM python:3.9.6-alpine3.13 as python
RUN mkdir /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENTRYPOINT [ "python", "-m", "zensearch.cli" ]
