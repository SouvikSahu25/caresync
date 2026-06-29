FROM python:3.13-alpine

WORKDIR /caresync

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S app && adduser -S -G app app
RUN chown -R app:app /caresync

EXPOSE 8000

USER app
CMD python manage.py migrate --noinput && \
    python seed_db.py && \
    exec python manage.py runserver 0.0.0.0:8000 --noreload