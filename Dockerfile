FROM python:3.12

WORKDIR /app

COPY requirements.txt /app/

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY entrypoint.sh /app/

RUN chmod +x ./entrypoint.sh

CMD ["/app/entrypoint.sh"]
