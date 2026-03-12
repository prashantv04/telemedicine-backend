from app.core.retry import retry_with_backoff


def send_booking_notification(email: str, consultation_id: str):
    # Here you would send an email, push notification, etc.
    def _send():
        print(f"Sending booking confirmation for consultation {consultation_id} to {email}")
        retry_with_backoff(_send)