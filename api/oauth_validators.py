from oauth2_provider.oauth2_validators import OAuth2Validator
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

class MyOAuth2Validator(OAuth2Validator):
    def validate_user(self, username, password, client, request, *args, **kwargs):
        # Aquí buscamos el usuario por email (que es username para ti)
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return False
        
        # Intentamos autenticar con email y password
        authenticated_user = authenticate(username=user.email, password=password)
        if authenticated_user is not None:
            request.user = authenticated_user
            return True
        return False
