import logging
import time

from django.conf import settings
from django.urls import reverse

import shopify
from ..models import Shop
from .login import create_shopify_session

logger = logging.getLogger(__name__)

def validate_params(request, params):
    """Validate the state and HMAC parameters from the Shopify request."""
    # # Validate state parameter
    # if request.META.get("HTTP_X_SHOPIFY_OAUTH_STATE_PARAM") != params.get("state"):
    #     logger.warning("Anti-forgery state parameter does not match.")
    #     raise ValueError("Anti-forgery state parameter does not match.")

    # Validate HMAC
    if not shopify.Session.validate_params(params):
        logger.warning("Invalid callback parameters.")
        raise ValueError("Invalid callback parameters.")


def exchange_code_for_access_token(request, shop):
    """Exchange the authorization code for an access token."""
    session = create_shopify_session(shop)
    access_token = session.request_token(request.query_params.dict())
    access_scopes = session.access_scopes

    return access_token, access_scopes


def store_shop_information(access_token, access_scopes, shop_domain):
    """Store or update shop information in the database."""
    current_timestamp = int(time.time())

    shop, created = Shop.objects.get_or_create(
        domain=shop_domain,
        defaults={
            'access_token': access_token,
            'access_scopes': access_scopes,
            'created_at': current_timestamp,
            'updated_at': current_timestamp
        }
    )

    if not created:
        shop.access_token = access_token
        shop.access_scopes = access_scopes
        shop.updated_at = current_timestamp
        shop.save()

    logger.info(f"{'Created' if created else 'Updated'} shop information for {shop_domain}.")


def shopify_session(shopify_domain, access_token):
    """Create a temporary Shopify session."""
    api_version = settings.SHOPIFY_API_VERSION
    return shopify.Session.temp(shopify_domain, api_version, access_token)


def get_api_endpoint(namespace):
    """Construct the full API endpoint URL for the given namespace."""
    api_url = settings.SHOPIFY_API_URL
    endpoint = api_url + reverse(namespace)
    return endpoint


def create_uninstall_webhook(shop, access_token):
    """Create a webhook for app uninstallation."""
    try:
        with shopify_session(shop, access_token):
            webhook = shopify.Webhook()
            webhook.topic = "app/uninstalled"
            webhook.address = get_api_endpoint('uninstall')
            webhook.format = "json"
            webhook.save()

        logger.info(f"Uninstall webhook created for shop: {shop}.")
    
    except Exception as e:
        logger.error(f"Failed to create uninstall webhook for shop {shop}: {e}")


def create_order_create_webhook(shop, access_token):
    """Create a webhook for new orders."""
    try:
        with shopify_session(shop, access_token):
            webhook = shopify.Webhook()
            webhook.topic = "orders/create"
            webhook.address = get_api_endpoint('webhook_order_create')
            webhook.format = "json"
            webhook.save()

        logger.info(f"Order creation webhook created for shop: {shop}.")

    except Exception as e:
        logger.error(f"Failed to create order creation webhook for shop {shop}: {e}")
