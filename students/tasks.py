from celery import shared_task
import time

@shared_task
def send_welcome_email_task(user_email):
    """Simulates a heavy background job like sending an email."""
    print(f"Starting email dispatch to {user_email}...")
    time.sleep(5)  # Simulate network latency
    print(f"Email successfully sent to {user_email}!")
    return f"Notification sent to {user_email}"