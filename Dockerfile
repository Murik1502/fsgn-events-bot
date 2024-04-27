FROM python

WORKDIR /bot

COPY . /bot/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
