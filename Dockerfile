FROM python:3.15.0b3-alpine

RUN addgroup -S app && adduser -S -G app app
USER app 

WORKDIR /caresync/
COPY . .

# install deps
RUN pip install django django-bootstrap4

# migration
RUN python manage.py migrate
RUN python seed_db.py

ENV DJANGO_DEBUG=False
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]