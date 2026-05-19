"""
Envía correos transaccionales usando el SDK oficial de Brevo.
Dependencia confirmada en requirements.txt: sib-api-v3-sdk==7.6.0
"""

import logging
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from decouple import config

logger = logging.getLogger(__name__)


def _get_api_instance():
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = config("BREVO_API_KEY")
    return sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )


def enviar_correo(destinatario: str, asunto: str, html: str) -> dict:
    """
    Envía un correo HTML al destinatario indicado.

    Returns:
        dict con 'exito' (bool) y 'error' (str | None).
    """
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": destinatario}],
        sender={
            "email": config("BREVO_SENDER_EMAIL"),
            "name": config("BREVO_SENDER_NAME", default="Agente de Precios"),
        },
        subject=asunto,
        html_content=html,
    )

    try:
        _get_api_instance().send_transac_email(send_smtp_email)
        logger.info("Correo enviado a %s | Asunto: %s", destinatario, asunto)
        return {"exito": True, "error": None}
    except ApiException as exc:
        logger.error("Error al enviar correo a %s: %s", destinatario, exc)
        return {"exito": False, "error": str(exc)}