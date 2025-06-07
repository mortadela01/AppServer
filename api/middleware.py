class LogRequestBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/o/token/' and request.method == 'POST':
            print(f"Body POST /o/token/: {request.body.decode('utf-8')}")
        return self.get_response(request)

class TokenDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/o/token/' and request.method == 'POST':
            print("=== /o/token/ REQUEST START ===")
            print("Headers:", dict(request.headers))
            print("Body:", request.body.decode('utf-8'))
            print("POST data:", request.POST)
            print("=== /o/token/ REQUEST END ===")
        return self.get_response(request)
    
# Middleware para capturar y validar el token Bearer
from oauth2_provider.models import AccessToken
from rest_framework.exceptions import AuthenticationFailed

class TokenValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificamos si la solicitud tiene el encabezado Authorization
        auth_header = request.headers.get('Authorization', None)
        if auth_header:
            # Extraemos el token Bearer
            try:
                token_type, token = auth_header.split(' ')
                if token_type.lower() != 'bearer':
                    raise AuthenticationFailed('Invalid token type')
                
                # Ahora verificamos si el token Bearer es válido
                try:
                    access_token = AccessToken.objects.get(token=token)
                except AccessToken.DoesNotExist:
                    raise AuthenticationFailed('Invalid or expired token')

                # Si el token es válido, lo añadimos al request
                request.user = access_token.user
                return self.get_response(request)
            
            except ValueError:
                raise AuthenticationFailed('Invalid Authorization header format')

        # Si no hay token o no es Bearer, rechazamos la solicitud
        raise AuthenticationFailed('Authorization token missing or invalid')

