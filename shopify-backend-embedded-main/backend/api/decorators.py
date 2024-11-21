from django.urls import reverse
from shopify import ApiAccess, Session, session_token
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Shop

HTTP_AUTHORIZATION_HEADER = "HTTP_AUTHORIZATION"

def session_token_required(function):
    def wrapper(*args, **kwargs):
        authorization_header = get_authorization_header(args[1])

        if not authorization_header:
            return Response({"error": "Authorization header is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_session_token = session_token.decode_from_header(
                authorization_header=authorization_header,
                api_key=settings.SHOPIFY_API_KEY,
                secret=settings.SHOPIFY_API_SECRET,
            )

            shop_domain = decoded_session_token.get("dest").removeprefix("https://")
            api_version = settings.SHOPIFY_API_VERSION
            access_token = Shop.objects.get(domain=shop_domain).access_token

            with Session.temp(shop_domain, api_version, access_token):
                return function(*args, **kwargs, shop_domain=shop_domain)

        except session_token.SessionTokenError:
            return Response({"error": "Invalid session token"}, status=status.HTTP_401_UNAUTHORIZED)

        except Shop.DoesNotExist:
            return Response({"error": "Shop not found for the provided domain"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"Unable to authenticate session tokens: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)

    return wrapper


def get_authorization_header(request):
    return request.META.get(HTTP_AUTHORIZATION_HEADER)
