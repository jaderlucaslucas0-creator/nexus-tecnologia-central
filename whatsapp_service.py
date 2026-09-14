"""Integração opcional com a WhatsApp Business Cloud API."""
import json
import os
import urllib.error
import urllib.request


class WhatsAppConfigurationError(RuntimeError):
    pass


def is_configured():
    return bool(
        os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()
        and os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    )


def send_text_message(to: str, message: str):
    token = os.environ.get("WHATSAPP_ACCESS_TOKEN", "").strip()
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "").strip()
    api_version = os.environ.get("WHATSAPP_API_VERSION", "v23.0").strip()

    if not token or not phone_number_id:
        raise WhatsAppConfigurationError(
            "Configure WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID."
        )
    if not to or not message:
        raise ValueError("Destinatário e mensagem são obrigatórios.")

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"WhatsApp API retornou HTTP {exc.code}: {detail[:500]}"
        ) from exc
