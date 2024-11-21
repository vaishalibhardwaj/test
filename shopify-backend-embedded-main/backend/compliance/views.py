import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.utils import webhook

logger = logging.getLogger(__name__)

class ComplianceWebhook(APIView):
    """Handle compliance-related webhook requests."""

    @method_decorator(csrf_exempt)
    def post(self, request):
        # Validate the webhook's authenticity
        if not webhook.validate_webhook(request):
            logger.warning("Invalid compliance webhook signature.")
            return Response({"error": "Invalid webhook signature"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            return Response(status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error processing compliance webhook: {e}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
