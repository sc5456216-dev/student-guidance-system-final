FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Run migrations and collect static files before starting the server
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --noinput

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "student_guidance_system.wsgi:application"]
