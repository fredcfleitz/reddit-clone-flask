FROM python
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD gunicorn app:app --bind 0.0.0.0:8000

