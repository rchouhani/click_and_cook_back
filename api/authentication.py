from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('auth_token')
        if not token:
            return None
        try:
            return self.authenticate_credentials(token)
        except Token.DoesNotExist:
            raise AuthenticationFailed('Invalid token in cookie')