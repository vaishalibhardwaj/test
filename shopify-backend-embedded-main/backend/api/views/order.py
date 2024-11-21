import logging
from datetime import datetime

from django.conf import settings
from django.db import connection, transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

import shopify

from ..models import Order, Shop, WebhookEvent
from ..decorators import session_token_required
from ..utils import webhook, db

logger = logging.getLogger(__name__)


class OrderCreateWebhook(APIView):
    """Handle Shopify 'order/create' webhook to store order data."""

    @method_decorator(csrf_exempt)
    def post(self, request):
        if not webhook.validate_webhook(request):
            logger.warning("Invalid webhook signature.")
            return Response({"error": "Invalid webhook signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            webhook_data = request.data
            shop_domain = request.META.get('HTTP_X_SHOPIFY_SHOP_DOMAIN')
            webhook_event_id = request.META.get('HTTP_X_SHOPIFY_EVENT_ID')
            current_timestamp = int(datetime.fromisoformat(webhook_data['created_at']).timestamp())

            if WebhookEvent.objects.filter(event_id=webhook_event_id).exists():
                logger.info(f"Ignoring duplicate webhook event: {webhook_event_id}")
                return Response(status=status.HTTP_200_OK)

            with transaction.atomic():
                shop = Shop.objects.get(domain=shop_domain)
                
                order = Order(
                    order_id=webhook_data['id'],
                    shop=shop,
                    created_at=current_timestamp,
                    currency=webhook_data['currency'],
                    current_subtotal_price=webhook_data['current_subtotal_price'],
                )
                order.save()

                webhook_event = WebhookEvent(
                    event_id=webhook_event_id,
                    created_at=current_timestamp,
                )
                webhook_event.save()

            return Response(status=status.HTTP_200_OK)

        except Shop.DoesNotExist:
            logger.error(f"Shop not found for domain: {shop_domain}")
            return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            logger.error(f"Missing required data in webhook payload: {e}")
            return Response({"error": f"Missing data: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing order webhook: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderList(APIView):
    """Fetch list of orders for a specific shop."""

    @session_token_required
    def get(self, request, shop_domain=None):
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT o.*, s.domain FROM api_order o
                        JOIN api_shop s ON o.shop_id = s.id
                        WHERE s.domain = %s
                        ''', [shop_domain]
                    )
                    results = db.dictfetchall(cursor)
        
            return Response({'orders': results}, status=status.HTTP_200_OK)

        except shopify.ShopifyException as e:
            logger.error(f"Shopify API error: {e}")
            return Response({"error": "Shopify API request failed"}, status=status.HTTP_502_BAD_GATEWAY)
        
        except Exception as e:
            logger.error(f"Error fetching orders for shop {shop_domain}: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
