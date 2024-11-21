import logging
from django.conf import settings

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import shopify

from ..decorators import session_token_required

shopify.Session.setup(api_key=settings.SHOPIFY_API_KEY, secret=settings.SHOPIFY_API_SECRET)

logger = logging.getLogger(__name__)

class ProductList(APIView):
    """Fetch list of products for a specific shop."""

    @session_token_required
    def get(self, request, shop_domain=None):
        try:
            products = shopify.Product.find()
            products_data = [product.to_dict() for product in products]

            return Response({'products': products_data}, status=status.HTTP_200_OK)

        except shopify.ShopifyException as e:
            logger.error(f"Shopify API error: {e}")
            return Response({"error": "Shopify API request failed"}, status=status.HTTP_502_BAD_GATEWAY)
        
        except Exception as e:
            logger.error(f"Error fetching products for shop {shop_domain}: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
