from app.core.logging import logger


def send_booking_notification(email: str, consultation_id: str):
    """
    Background task for booking notification.
    In production this could send email, SMS, or push notification.
    """
    logger.info(
        f"Sending booking confirmation for consultation {consultation_id} to {email}"
    )