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