
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

# APP VR

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connection

# class UserIdByQrCodeView(APIView):
#     def get(self, request, qr_code):
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT id_user, visualization_status
#                 FROM TBL_QR
#                 WHERE qr_code = %s
#             """, [qr_code])
#             row = cursor.fetchone()
#         if row:
#             return Response({'id_user': row[0], 'visualization_status': row[1]})
#         elif row and row[1] == "private": # impedir la vizualización para el caso en que el codigo sea privado
#             return Response({'detail': 'The visualization of this code is "PRIVATE"'}, status=404)
#         return Response({'detail': 'QR code not found'}, status=404)

from oauthlib.common import generate_token
from oauth2_provider.models import AccessToken, Application, RefreshToken
from django.utils import timezone
from datetime import timedelta

class UserIdByQrCodeView(APIView):
    permission_classes = [permissions.AllowAny] 

    def get(self, request, qr_code):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_user, visualization_status
                FROM TBL_QR
                WHERE qr_code = %s
            """, [qr_code])
            row = cursor.fetchone()
        
        if row:
            id_user, visualization_status = row
            if visualization_status == "private":
                return Response({'detail': 'The visualization of this code is "PRIVATE"'}, status=404)
            
            # Generar token OAuth para este usuario
            try:
                app = Application.objects.get(name='Mausoleum API')
            except Application.DoesNotExist:
                return Response({'error': 'OAuth application not found'}, status=500)
            
            user_model = get_user_model()
            try:
                user = user_model.objects.get(pk=id_user)
            except user_model.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
            
            expires = timezone.now() + timedelta(seconds=36000)
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

            return Response({
                'id_user': id_user,
                'visualization_status': visualization_status,
                'access_token': access_token.token,
                'expires_in': 36000,
                'refresh_token': refresh_token.token,
                'token_type': 'Bearer',
                'scope': 'read write'
            })
        else:
            return Response({'detail': 'QR code not found'}, status=404)


class DeceasedByUserView(APIView):
    def get(self, request, user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT d.id_deceased, d.name, d.date_birth, d.date_death, d.description, d.burial_place, d.visualization_state, d.visualization_code
                FROM TBL_DECEASED d
                JOIN TBL_USER_DECEASED ud ON d.id_deceased = ud.id_deceased
                WHERE ud.id_user = %s
            """, [user_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(results)

class ImagesByDeceasedView(APIView):
    def get(self, request, deceased_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT img.id_image, img.image_link, img.event_title, img.description, imd.date_created, imd.coordinates
                FROM TBL_DECEASED_IMAGE di
                JOIN TBL_IMAGE img ON di.id_image = img.id_image
                JOIN TBL_IMAGE_METADATA imd ON di.id_metadata = imd.id_metadata
                WHERE di.id_deceased = %s
                ORDER BY imd.date_created ASC
            """, [deceased_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(results)

class VideosByDeceasedView(APIView):
    def get(self, request, deceased_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT vid.id_video, vid.video_link, vid.event_title, vid.description, vmd.date_created, vmd.coordinates
                FROM TBL_DECEASED_VIDEO dv
                JOIN TBL_VIDEO vid ON dv.id_video = vid.id_video
                JOIN TBL_VIDEO_METADATA vmd ON dv.id_metadata = vmd.id_metadata
                WHERE dv.id_deceased = %s
                ORDER BY vmd.date_created ASC
            """, [deceased_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(results)

class RelationsByDeceasedView(APIView):
    def get(self, request, deceased_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.id_parent, d.name AS parent_name, rt.relationship
                FROM TBL_RELATION r
                JOIN TBL_RELATIONSHIP_TYPE rt ON r.relationship = rt.relationship
                JOIN TBL_DECEASED d ON r.id_parent = d.id_deceased
                WHERE r.id_deceased = %s
            """, [deceased_id])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return Response(results)


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