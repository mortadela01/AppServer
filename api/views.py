
from rest_framework import permissions
from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *

import json
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from oauth2_provider.models import AccessToken, Application, RefreshToken
from django.utils import timezone
from datetime import timedelta

# User CRUD
class UserListCreate(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            # Permitir crear sin autenticación
            return [permissions.AllowAny()]
        # Para otros métodos, requiere autenticación
        return [permissions.IsAuthenticated()]

class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Deceased CRUD

class DeceasedListCreate(generics.ListCreateAPIView):
    queryset = Deceased.objects.all()
    serializer_class = DeceasedSerializer

class DeceasedRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Deceased.objects.all()
    serializer_class = DeceasedSerializer

# Video CRUD

class VideoListCreate(generics.ListCreateAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class VideoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

class VideoMetadataListCreate(generics.ListCreateAPIView):
    queryset = VideoMetadata.objects.all()
    serializer_class = VideoMetadataSerializer

class VideoMetadataRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoMetadata.objects.all()
    serializer_class = VideoMetadataSerializer

# DeceasedVideo

class DeceasedVideoListCreate(generics.ListCreateAPIView):
    queryset = DeceasedVideo.objects.all()
    serializer_class = DeceasedVideoSerializer

class DeceasedVideoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeceasedVideo.objects.all()
    serializer_class = DeceasedVideoSerializer

# Image CRUD

class ImageListCreate(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class ImageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class ImageMetadataListCreate(generics.ListCreateAPIView):
    queryset = ImageMetadata.objects.all()
    serializer_class = ImageMetadataSerializer

class ImageMetadataRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = ImageMetadata.objects.all()
    serializer_class = ImageMetadataSerializer

# DecesedImage CRUD

class DeceasedImageListCreate(generics.ListCreateAPIView):
    queryset = DeceasedImage.objects.all()
    serializer_class = DeceasedImageSerializer

class DeceasedImageRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeceasedImage.objects.all()
    serializer_class = DeceasedImageSerializer

# Relationship and Type CRUD

class RelationshipTypeListCreate(generics.ListCreateAPIView):
    queryset = RelationshipType.objects.all()
    serializer_class = RelationshipTypeSerializer

class RelationshipTypeRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = RelationshipType.objects.all()
    serializer_class = RelationshipTypeSerializer

class RelationListCreate(generics.ListCreateAPIView):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer

class RelationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer

# UserDeceased CRUD

class UserDeceasedListCreate(generics.ListCreateAPIView):
    queryset = UserDeceased.objects.all()
    serializer_class = UserDeceasedSerializer

class UserDeceasedRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserDeceased.objects.all()
    serializer_class = UserDeceasedSerializer

# Request CRUD

class RequestListCreate(generics.ListCreateAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class RequestRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

# Notify CRUD

class NotificationListCreate(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class NotificationRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
# QR CRUD

class QRListCreate(generics.ListCreateAPIView):
    queryset = QR.objects.all()
    serializer_class = QRSerializer

class QRRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = QR.objects.all()
    serializer_class = QRSerializer

# Google AUTH

User = get_user_model()

def google_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    token = body.get('id_token')
    if not token:
        return JsonResponse({'error': 'id_token missing'}, status=400)

    try:
        # Verificar token con Google
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), '776557165549-k3a59gfcinfnqfd67un5hufctjo4goht.apps.googleusercontent.com')
        email = idinfo['email']
    except ValueError:
        return JsonResponse({'error': 'Invalid token'}, status=400)

    user, created = User.objects.get_or_create(email=email)
    if created:
        user.set_unusable_password()
        user.save()

    try:
        app = Application.objects.get(name='Mausoleum API')
    except Application.DoesNotExist:
        return JsonResponse({'error': 'OAuth application not found'}, status=500)

    expires = timezone.now() + timedelta(seconds=36000)

    # access_token = AccessToken.objects.create(
    #     user=user,
    #     application=app,
    #     # token=AccessToken.generate_token(),
    #     token=generate_token(),
    #     expires=expires,
    #     scope='read write'
    # )
    # refresh_token = RefreshToken.objects.create(
    #     user=user,
    #     # token=RefreshToken.generate_token(),
    #     token=generate_token(),
    #     application=app,
    #     access_token=access_token
    # )

    from oauthlib.common import generate_token


    access_token_str = generate_token()
    refresh_token_str = generate_token()


    access_token = AccessToken.objects.create(
    user=user,
    application=app,
    token=access_token_str,
    expires=expires,
    scope='read write'
    )
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=refresh_token_str,
        application=app,
        access_token=access_token
    )



    return JsonResponse({
        'access_token': access_token.token,
        'expires_in': 36000,
        'refresh_token': refresh_token.token,
        'token_type': 'Bearer',
        'scope': 'read write'
    })