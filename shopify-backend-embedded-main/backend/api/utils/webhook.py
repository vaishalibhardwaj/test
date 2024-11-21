import hashlib
import base64
import hmac
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

def validate_hmac(body, secret, hmac_to_verify):
    """Validate the HMAC of the request body against the expected HMAC."""
    hashed = hmac.new(secret.encode('utf-8'), body, hashlib.sha256)
    hmac_calculated = base64.b64encode(hashed.digest()).decode('utf-8')
    return hmac_calculated == hmac_to_verify


def validate_webhook(request):
    """Validate the Shopify webhook by checking its HMAC signature."""
    try:
        webhook_hmac = request.META.get('HTTP_X_SHOPIFY_HMAC_SHA256')
        webhook_data = request.body
        
        if not webhook_hmac:
            logger.warning("Missing HMAC in request headers.")
            return False

        return validate_hmac(webhook_data, settings.SHOPIFY_API_SECRET, webhook_hmac)

    except Exception as e:
        logger.error(f"Error validating webhook: {e}")
        return False
