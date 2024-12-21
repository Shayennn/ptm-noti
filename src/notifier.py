import apprise

from config import Config
from logger import log_json


def send_notification(message, attachments=None):
    """
    Send notifications using Apprise.
    :param message: The notification message.
    :param attachments: List of file paths to attach.
    """
    if not Config.APPRISE_URL:
        log_json(40, "No APPRISE_URL configured; skipping notification")
        return

    apobj = apprise.Apprise()
    apobj.add(Config.APPRISE_URL)

    try:
        # Send the notification with optional attachments
        success = apobj.notify(
            body=message,
            title="New Ticket Notification",
            attach=attachments or [],  # Apprise expects file paths for attachments
        )
        if success:
            log_json(
                20, "Notification sent successfully", message=message, attachments=attachments or []
            )
        else:
            log_json(
                40, "Failed to send notification", message=message, attachments=attachments or []
            )
    except Exception as e:
        log_json(40, "Failed to send notification", error=str(e))
