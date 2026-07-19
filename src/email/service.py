import sib_api_v3_sdk

from sib_api_v3_sdk.rest import ApiException

from src.utils.settings import settings
from src.utils.logger import logger

configuration = sib_api_v3_sdk.Configuration()

configuration.api_key["api-key"] = settings.BREVO_API_KEY

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)



def send_email(
    to_email: str,
    subject: str,
    html: str,
):
    sender = {
        "name": settings.EMAIL_FROM_NAME,
        "email": settings.EMAIL_FROM,
    }

    receiver = [
        {
            "email": to_email,
        }
    ]

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=receiver,
        subject=subject,
        html_content=html,
    )

    try:
        response = api_instance.send_transac_email(email)

        logger.info(
            f"Email sent successfully to {to_email}"
        )

        return response

    except ApiException as e:
        logger.exception(
            f"Failed to send email to {to_email}: {e}"
        )

        return None