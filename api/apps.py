# from django.apps import AppConfig


# class ApiConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'api'

from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        import oauth2_provider.views.base as base_views
        original_post = base_views.TokenView.post

        def debug_post(self, request, *args, **kwargs):
            print("=== TokenView POST ===")
            print("request.POST:", request.POST)
            print("request.body:", request.body.decode('utf-8'))
            result = original_post(self, request, *args, **kwargs)
            print("=== TokenView POST result status:", result.status_code)
            return result

        base_views.TokenView.post = debug_post