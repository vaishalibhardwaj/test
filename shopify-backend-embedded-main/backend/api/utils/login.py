import binascii
import os
import logging

from django.conf import settings
from django.urls import reverse
from rest_framework.response import Response
from rest_framework import status

import shopify
from shopify.utils import shop_url

from ..models import Shop

logger = logging.getLogger(__name__)

def authenticate(request):
    """Authenticate the shop and create a permission URL."""
    try:
        shop = get_sanitized_shop_domain(request)
        
        scopes, redirect_uri, state = create_auth_params()
        permission_url = create_shopify_session(shop).create_permission_url(
            scopes, redirect_uri, state
        )
        try:
            shop_data = Shop.objects.get(domain=shop)
            if shop_data.access_token:
                return Response({'authenticated': True, "url": permission_url, "shopify_oauth_state_param": state}, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            pass
        return Response({'authenticated': False, "url": permission_url, "shopify_oauth_state_param": state}, status=status.HTTP_200_OK)
    
    except ValueError as exception:
        logger.warning(f"Authentication failed: {str(exception)}")
        return Response({"error": str(exception)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_sanitized_shop_domain(request):
    """Retrieve and sanitize the shop domain from the request."""
    shop = request.query_params.get('shop')
    sanitized_shop_domain = shop_url.sanitize_shop_domain(shop)

    if not sanitized_shop_domain:
        logger.warning("Invalid shop domain format.")
        raise ValueError("Shop domain must match 'example.myshopify.com'.")
    
    return sanitized_shop_domain


def create_auth_params():
    """Create authorization parameters for the Shopify OAuth process."""
    scopes = settings.SHOPIFY_API_SCOPES.split(",")
    
    redirect_uri = settings.SHOPIFY_API_URL + reverse('callback')
    # redirect_uri = f'{settings.SHOPIFY_APP_URL}/shopify-callback'

    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")

    return scopes, redirect_uri, state


def create_shopify_session(shop_domain_url):
    """Create a new Shopify session for the specified shop URI."""
    shopify_api_version = settings.SHOPIFY_API_VERSION
    shopify_api_key = settings.SHOPIFY_API_KEY
    shopify_api_secret = settings.SHOPIFY_API_SECRET

    shopify.Session.setup(api_key=shopify_api_key, secret=shopify_api_secret)
    return shopify.Session(shop_domain_url, shopify_api_version)
