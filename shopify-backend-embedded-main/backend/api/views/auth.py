import logging
from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from ..models import Shop
from ..utils import login, callback

logger = logging.getLogger(__name__)

class Login(APIView):
    """Handle Shopify authentication login."""

    def get(self, request):
        shop = request.query_params.get('shop')
        if not shop:
            return Response({"error": "Shop domain is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            return login.authenticate(request)
        except Exception as e:
            logger.error(f"Authentication failed for shop {shop}: {e}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            return login.authenticate(request)
        except Exception as e:
            logger.error(f"Authentication failed during POST request: {e}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Callback(APIView):
    """Handle Shopify OAuth callback and data storage."""

    def get(self, request):
        params = request.query_params
        shop = params.get("shop")

        if not shop:
            return Response({"error": "Shop domain is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                callback.validate_params(request, params)
                access_token, access_scopes = callback.exchange_code_for_access_token(request, shop)
                callback.store_shop_information(access_token, access_scopes, shop)
                callback.create_uninstall_webhook(shop, access_token)
                callback.create_order_create_webhook(shop, access_token)

            redirect_uri = f"{settings.SHOPIFY_APP_URL}?shop={shop}"
            # return Response({
            #     "success": True,
            #     "redirect_uri": redirect_uri,
            #     "accessToken": access_token,
            #     "shop": shop
            # }, status=status.HTTP_200_OK)
            return HttpResponseRedirect(redirect_uri)

        except ValidationError as ve:
            logger.warning(f"Validation error for shop {shop}: {ve}")
            return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as ve:
            logger.warning(f"Invalid data for shop {shop}: {ve}")
            return Response({"error": "Invalid request data"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Callback processing failed for shop {shop}: {e}")
            return Response({"error": "Callback processing failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Uninstall(APIView):
    """Handle uninstall webhook from Shopify."""

    @method_decorator(csrf_exempt)
    def post(self, request):
        uninstall_data = request.data
        shop_domain = uninstall_data.get("domain")

        if not shop_domain:
            return Response({"error": "Domain is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Shop.objects.filter(domain=shop_domain).delete()
            logger.info(f"Shop with domain {shop_domain} uninstalled successfully.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Failed to uninstall shop {shop_domain}: {e}")
            return Response({"error": "Uninstall failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
