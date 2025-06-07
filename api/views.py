
from rest_framework import permissions
from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser

import json
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google.auth.transport import requests
from django.contrib.auth import get_user_model
from oauth2_provider.models import AccessToken, Application, RefreshToken
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection, transaction
from .serializers import DeceasedSerializer, RelationSerializer, UserDeceasedSerializer
from .models import User, Deceased
import re
from django.contrib.auth import authenticate

from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings


@method_decorator(csrf_exempt, name='dispatch')  # Para evitar problemas con CSRF en login
class OAuth2PasswordLoginView(APIView):
    permission_classes = []  # Sin restricciones para login

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=password)
        if user is None:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            app = Application.objects.get(name='Mausoleum API')
        except Application.DoesNotExist:
            return Response({'error': 'OAuth application not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            'access_token': access_token.token,
            'expires_in': 36000,
            'refresh_token': refresh_token.token,
            'token_type': 'Bearer',
            'scope': 'read write'
        })

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

# views.py (appServer)

# class UserByEmailView(APIView):
#     permission_classes = []  # O protección según convenga

#     def get(self, request):
#         email = request.GET.get('email')
#         if not email:
#             return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         User = get_user_model()
#         try:
#             user = User.objects.get(email=email)
#             return Response({
#                 'id_user': user.id_user,
#                 'name': user.name,
#                 'email': user.email,
#             }, status=status.HTTP_200_OK)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class UserByEmailView(APIView):
    permission_classes = []  # Opcional protección

    def get(self, request):
        email = request.GET.get('email')
        if not email:
            return Response({'error': 'Email parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        User = get_user_model()
        try:
            user = User.objects.get(email=email)

            # Obtener la aplicación OAuth
            try:
                app = Application.objects.get(name='Mausoleum API')
            except Application.DoesNotExist:
                return Response({'error': 'OAuth application not found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Eliminar tokens previos para evitar acumulación (opcional)
            AccessToken.objects.filter(user=user, application=app).delete()
            RefreshToken.objects.filter(user=user, application=app).delete()

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
                'id_user': user.id_user,
                'name': user.name,
                'email': user.email,
                'access_token': access_token.token,
                'expires_in': 36000,
                'refresh_token': refresh_token.token,
                'token_type': 'Bearer',
                'scope': 'read write',
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

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

import logging
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Video
from .serializers import VideoSerializer

logger = logging.getLogger(__name__)

class VideoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        # print(f"📥 GET request received for Video ID: {video_id}")
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        # print(f"🛠 PUT request for Video ID: {video_id}")
        # print(f"🧾 Data received: {request.data}")
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        # print(f"🩹 PATCH request for Video ID: {video_id}")
        # print(f"📦 Partial data received: {request.data}")
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        video_id = kwargs.get('pk')
        # print(f"❌ DELETE request for Video ID: {video_id}")
        return super().delete(request, *args, **kwargs)


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

    def get(self, request, *args, **kwargs):
        image_id = kwargs.get('pk')
        # print(f"📥 [GET] Image ID: {image_id}")
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        image_id = kwargs.get('pk')
        # print(f"🛠 [PUT] Image ID: {image_id}")
        # print(f"🧾 [PUT] Data received: {request.data}")

        response = super().put(request, *args, **kwargs)

        # if hasattr(response, 'data'):
        #     # print(f"✅ [PUT] Serializer response: {response.data}")
        # elif hasattr(response, 'status_code') and response.status_code >= 400:
        #     # print(f"❗ [PUT] Response Error: status_code={response.status_code}, content={getattr(response, 'data', 'N/A')}")

        return response

    def patch(self, request, *args, **kwargs):
        image_id = kwargs.get('pk')
        # print(f"🩹 [PATCH] Image ID: {image_id}")
        # print(f"📦 [PATCH] Data received: {request.data}")
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        image_id = kwargs.get('pk')
        # print(f"❌ [DELETE] Image ID: {image_id}")
        return super().delete(request, *args, **kwargs)

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


# ----------------------- APP WEB

class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = []
        unread_count = 0

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM TBL_NOTIFICATION WHERE id_receiver = %s ORDER BY creation_date DESC
            """, [user.id_user])
            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                notif = dict(zip(columns, row))
                match = re.search(r"Request #(\d+)", notif.get("message", ""))
                if match:
                    notif["request_id"] = match.group(1)
                notifications.append(notif)

            cursor.execute("""
                SELECT COUNT(*) FROM TBL_NOTIFICATION WHERE id_receiver = %s AND is_read = 0
            """, [user.id_user])
            unread_count = cursor.fetchone()[0]

        user_data = {
            "id_user": user.id_user,
            "name": user.name,
            "email": user.email,
        }

        return Response({
            "user": user_data,
            "notifications": notifications,
            "unread_count": unread_count
        })


from rest_framework.parsers import MultiPartParser, FormParser

class AddFamilyMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # para recibir multipart/form-data

    @transaction.atomic
    def post(self, request):
        data = request.data  # llega como QueryDict

        # 1) Crear el modelo Deceased, copiando la lógica de “form.save(commit=False) + descripción desde 'biography'”
        deceased_data = {
            'name': data.get('name'),
            'date_birth': data.get('date_birth'),
            'date_death': data.get('date_death'),
            # En la versión monolítica hacías: new_deceased.description = request.POST.get('biography', '')
            'description': data.get('biography', ''),          # <-- aquí usamos 'biography'
            'burial_place': data.get('burial_place'),
            'visualization_state': data.get('visualization_state', True),
            'visualization_code': data.get('visualization_code'),
        }

        serializer = DeceasedSerializer(data=deceased_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_deceased = serializer.save()
        deceased_id = new_deceased.id_deceased

        # 2) Insertar relaciones en TBL_RELATION (idéntico al monolito)
        related_ids = data.getlist('related_deceased[]')
        relationship_types = data.getlist('relationship_type[]')
        if related_ids and relationship_types and len(related_ids) == len(relationship_types):
            with connection.cursor() as cursor:
                for related_id, rel_type in zip(related_ids, relationship_types):
                    if related_id and rel_type:
                        cursor.execute("""
                            INSERT INTO TBL_RELATION (id_deceased, id_parent, relationship)
                            VALUES (%s, %s, %s)
                        """, [deceased_id, int(related_id), rel_type])

        # 3) Insertar vínculo en TBL_USER_DECEASED (usuario autenticado tiene permisos)
        user = request.user
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                VALUES (%s, %s, %s, %s)
            """, [user.id_user, deceased_id, timezone.now(), 1])

        # 4) Procesar imágenes (idéntico al flujo del monolito, mismo orden de inserts)
        fs_images = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'images'))
        images = request.FILES.getlist('images')
        for idx, image_file in enumerate(images):
            filename = fs_images.save(image_file.name, image_file)
            uploaded_file_url = fs_images.url(filename)
            event_title = data.get(f'image_event_{idx}', '')
            description = data.get(f'image_desc_{idx}', '')

            with connection.cursor() as cursor:
                # 4.1) Insertar metadato en TBL_IMAGE_METADATA
                cursor.execute("""
                    INSERT INTO TBL_IMAGE_METADATA (date_created, coordinates)
                    VALUES (%s, %s)
                """, [timezone.now(), ""])
                metadata_id = cursor.lastrowid

                # 4.2) Insertar vínculo en la tabla puente TBL_DECEASED_IMAGE
                cursor.execute("""
                    INSERT INTO TBL_DECEASED_IMAGE (id_deceased, id_metadata, image_link)
                    VALUES (%s, %s, %s)
                """, [deceased_id, metadata_id, uploaded_file_url])

                # 4.3) Finalmente, insertar el registro en TBL_IMAGE
                cursor.execute("""
                    INSERT INTO TBL_IMAGE (id_image, image_link, event_title, description)
                    VALUES (%s, %s, %s, %s)
                """, [metadata_id, uploaded_file_url, event_title, description])

        # 5) Procesar vídeos (idéntico al flujo del monolito, mismo orden de inserts)
        fs_videos = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'videos'))
        video_files = request.FILES.getlist('videos')
        for idx, video_file in enumerate(video_files):
            filename = fs_videos.save(video_file.name, video_file)
            uploaded_file_url = fs_videos.url(filename)
            event_title = data.get(f'video_event_{idx}', '')
            description = data.get(f'video_desc_{idx}', '')

            with connection.cursor() as cursor:
                # 5.1) Insertar metadato en TBL_VIDEO_METADATA
                cursor.execute("""
                    INSERT INTO TBL_VIDEO_METADATA (date_created, coordinates)
                    VALUES (%s, %s)
                """, [timezone.now(), ""])
                metadata_id = cursor.lastrowid

                # 5.2) Insertar vínculo en la tabla puente TBL_DECEASED_VIDEO
                cursor.execute("""
                    INSERT INTO TBL_DECEASED_VIDEO (id_deceased, id_metadata, video_link)
                    VALUES (%s, %s, %s)
                """, [deceased_id, metadata_id, uploaded_file_url])

                # 5.3) Finalmente, insertar el registro en TBL_VIDEO
                cursor.execute("""
                    INSERT INTO TBL_VIDEO (id_video, video_link, event_title, description)
                    VALUES (%s, %s, %s, %s)
                """, [metadata_id, uploaded_file_url, event_title, description])

        # 6) Devolver el objeto creado (igual que en el monolito hacías redirect, aquí devolvemos JSON)
        return Response(DeceasedSerializer(new_deceased).data, status=status.HTTP_201_CREATED)

class FamilyMemberListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        miembros = []
        permisos = []
        otros_deceased = []
        notifications = []
        unread_count = 0

        with connection.cursor() as cursor:
            # 1) Obtener fallecidos relacionados al usuario
            cursor.execute("""
                SELECT d.id_deceased, d.name, d.date_birth, d.date_death, d.burial_place, ud.has_permission 
                FROM TBL_DECEASED d
                INNER JOIN TBL_USER_DECEASED ud ON d.id_deceased = ud.id_deceased
                WHERE ud.id_user = %s
            """, [user.id_user])

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                miembro = dict(zip(columns, row))
                permisos.append(miembro['has_permission'])

                deceased_id = miembro['id_deceased']

                # 1.a) Obtener imágenes de este fallecido
                cursor.execute("""
                    SELECT im.id_metadata, i.image_link, i.event_title, i.description
                    FROM TBL_DECEASED_IMAGE im
                    JOIN TBL_IMAGE i ON im.id_metadata = i.id_image
                    WHERE im.id_deceased = %s
                    ORDER BY i.id_image ASC
                """, [deceased_id])
                image_columns = [col[0] for col in cursor.description]
                images = [dict(zip(image_columns, img_row)) for img_row in cursor.fetchall()]

                # 1.b) Obtener vídeos de este fallecido
                cursor.execute("""
                    SELECT vm.id_metadata, v.video_link, v.event_title, v.description
                    FROM TBL_DECEASED_VIDEO vm
                    JOIN TBL_VIDEO v ON vm.id_metadata = v.id_video
                    WHERE vm.id_deceased = %s
                    ORDER BY v.id_video ASC
                """, [deceased_id])
                video_columns = [col[0] for col in cursor.description]
                videos = [dict(zip(video_columns, vid_row)) for vid_row in cursor.fetchall()]

                # 1.c) Agregar listas de imágenes y vídeos al miembro
                miembro['images'] = images
                miembro['videos'] = videos

                miembros.append(miembro)

            # 2) Obtener otros fallecidos no relacionados al usuario
            cursor.execute("""
                SELECT *
                FROM TBL_DECEASED
                WHERE id_deceased NOT IN (
                    SELECT id_deceased FROM TBL_USER_DECEASED WHERE id_user = %s
                )
            """, [user.id_user])

            other_columns = [col[0] for col in cursor.description]
            otros_deceased = [dict(zip(other_columns, row)) for row in cursor.fetchall()]

            # 3) Obtener notificaciones del usuario
            cursor.execute("""
                SELECT id_notification, id_sender, message, is_read, creation_date
                FROM TBL_NOTIFICATION
                WHERE id_receiver = %s
                ORDER BY creation_date DESC
            """, [user.id_user])
            notif_columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                notif = dict(zip(notif_columns, row))
                # Extraer “Request #ID” si existe en el mensaje
                import re
                match = re.search(r"Request #(\d+)", notif.get("message", ""))
                if match:
                    notif["request_id"] = match.group(1)
                notifications.append(notif)

            # 4) Contar notificaciones sin leer
            cursor.execute("""
                SELECT COUNT(*) FROM TBL_NOTIFICATION
                WHERE id_receiver = %s AND is_read = 0
            """, [user.id_user])
            unread_count = cursor.fetchone()[0]

        return Response({
            "miembros": miembros,
            "permisos": permisos,
            "otros_deceased": otros_deceased,
            "notifications": notifications,
            "unread_count": unread_count,
        })

class ShareFamilyMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        email = request.data.get('email')
        if not email:
            return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        shared_user = User.objects.filter(email=email).first()
        sender = request.user

        if not shared_user:
            return Response({"email": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TBL_NOTIFICATION (id_sender, id_receiver, message, is_read, creation_date)
                VALUES (%s, %s, %s, %s, %s)
            """, [
                sender.id_user,
                shared_user.id_user,
                f"{sender.name} has shared memory ID {id} with you. Do you approve?",
                0,
                timezone.now()
            ])

        return Response({"detail": "Memory shared successfully."}, status=status.HTTP_200_OK)

# class EditFamilyMemberView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]   # <— importante para recibir archivos y form-data

#     @transaction.atomic
#     def put(self, request, id):
#         # 1) Obtener objeto Deceased o 404
#         miembro = get_object_or_404(Deceased, id_deceased=id)
#         user = request.user

#         # 2) Verificar que el usuario tenga permiso en TBL_USER_DECEASED
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT has_permission FROM TBL_USER_DECEASED
#                 WHERE id_user = %s AND id_deceased = %s
#             """, [user.id_user, id])
#             perm = cursor.fetchone()
#             if not perm:
#                 return Response({"detail": "No permission to edit this deceased."},
#                                 status=status.HTTP_403_FORBIDDEN)

#         # 3) Usar DeceasedSerializer para actualizar los campos principales
#         #    (name, date_birth, date_death, description, burial_place, visualization_state, visualization_code)
#         serializer = DeceasedSerializer(miembro, data=request.data, partial=True)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         serializer.save()

#         # 4) Manejo de relaciones en TBL_RELATION
#         related_ids = request.data.getlist('related_deceased[]')
#         relationship_types = request.data.getlist('relationship_type[]')
#         deleted_relation_ids = request.data.getlist('deleted_relation_ids[]')

#         with connection.cursor() as cursor:
#             # - Eliminar relaciones marcadas para borrar
#             for del_id in deleted_relation_ids:
#                 cursor.execute("""
#                     DELETE FROM TBL_RELATION
#                     WHERE id_deceased = %s AND id_parent = %s
#                 """, [id, del_id])

#             # - Obtener relaciones existentes
#             cursor.execute("SELECT id_parent FROM TBL_RELATION WHERE id_deceased = %s", [id])
#             existing_ids = set(row[0] for row in cursor.fetchall())

#             # - Insertar relaciones nuevas si no existen
#             for related_id, rel_type in zip(related_ids, relationship_types):
#                 if related_id and rel_type and int(related_id) not in existing_ids:
#                     cursor.execute("""
#                         INSERT INTO TBL_RELATION (id_deceased, id_parent, relationship)
#                         VALUES (%s, %s, %s)
#                     """, [id, int(related_id), rel_type])

#         # 5) Manejo de imágenes
#         #    5.1) Borrar las que vienen en delete_image_ids[]
#         #    5.2) Actualizar event_title/description de existing_image_id[]
#         #    5.3) Guardar nuevas imágenes de request.FILES.getlist('images')
#         with connection.cursor() as cursor:
#             # 5.1) Eliminar imágenes marcadas
#             delete_image_ids = request.data.getlist('delete_image_ids[]')
#             for del_id in delete_image_ids:
#                 # quitar vínculo en la tabla puente y eliminar registros de imagen
#                 cursor.execute("DELETE FROM TBL_DECEASED_IMAGE WHERE id_metadata = %s", [del_id])
#                 cursor.execute("DELETE FROM TBL_IMAGE WHERE id_image = %s", [del_id])

#             # 5.2) Actualizar las etiquetas de las imágenes existentes
#             existing_image_ids = request.data.getlist('existing_image_id[]')
#             for idx, img_id in enumerate(existing_image_ids):
#                 event = request.data.get(f'existing_image_event_{idx}', '')   # nombre del campo en el form
#                 desc = request.data.get(f'existing_image_desc_{idx}', '')
#                 cursor.execute("""
#                     UPDATE TBL_IMAGE
#                     SET event_title = %s,
#                         description = %s
#                     WHERE id_image = %s
#                 """, [event, desc, img_id])

#             # 5.3) Guardar nuevas imágenes
#             fs_imagenes = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'images'))
#             for idx, image_file in enumerate(request.FILES.getlist('images')):
#                 filename = fs_imagenes.save(image_file.name, image_file)
#                 uploaded_file_url = fs_imagenes.url(filename)
#                 event = request.data.get(f'image_event_{idx}', '')
#                 desc = request.data.get(f'image_desc_{idx}', '')

#                 # - Creamos un registro en TBL_IMAGE_METADATA
#                 cursor.execute("""
#                     INSERT INTO TBL_IMAGE_METADATA (date_created, coordinates)
#                     VALUES (%s, %s)
#                 """, [timezone.now(), ""])
#                 metadata_id = cursor.lastrowid

#                 # - Insertar vínculo en la tabla puente
#                 cursor.execute("""
#                     INSERT INTO TBL_DECEASED_IMAGE (id_deceased, id_metadata, image_link)
#                     VALUES (%s, %s, %s)
#                 """, [id, metadata_id, uploaded_file_url])

#                 # - Insertar el registro en TBL_IMAGE
#                 cursor.execute("""
#                     INSERT INTO TBL_IMAGE (id_image, image_link, event_title, description)
#                     VALUES (%s, %s, %s, %s)
#                 """, [metadata_id, uploaded_file_url, event, desc])

#         # 6) Manejo de vídeos (igual que imágenes)
#         with connection.cursor() as cursor:
#             # 6.1) Eliminar vídeos marcados
#             delete_video_ids = request.data.getlist('delete_video_ids[]')
#             for del_id in delete_video_ids:
#                 cursor.execute("DELETE FROM TBL_DECEASED_VIDEO WHERE id_metadata = %s", [del_id])
#                 cursor.execute("DELETE FROM TBL_VIDEO WHERE id_video = %s", [del_id])

#             # 6.2) Actualizar metadata de vídeos existentes
#             existing_video_ids = request.data.getlist('existing_video_id[]')
#             for idx, vid_id in enumerate(existing_video_ids):
#                 event = request.data.get(f'existing_video_event_{idx}', '')
#                 desc = request.data.get(f'existing_video_desc_{idx}', '')
#                 cursor.execute("""
#                     UPDATE TBL_VIDEO
#                     SET event_title = %s,
#                         description = %s
#                     WHERE id_video = %s
#                 """, [event, desc, vid_id])

#             # 6.3) Guardar nuevos vídeos
#             fs_videos = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'videos'))
#             for idx, video_file in enumerate(request.FILES.getlist('videos')):
#                 filename = fs_videos.save(video_file.name, video_file)
#                 uploaded_video_url = fs_videos.url(filename)
#                 event = request.data.get(f'video_event_{idx}', '')
#                 desc = request.data.get(f'video_desc_{idx}', '')

#                 # - Insertar metadato en TBL_VIDEO_METADATA
#                 cursor.execute("""
#                     INSERT INTO TBL_VIDEO_METADATA (date_created, coordinates)
#                     VALUES (%s, %s)
#                 """, [timezone.now(), ""])
#                 metadata_id = cursor.lastrowid

#                 # - Insertar vínculo en la tabla puente
#                 cursor.execute("""
#                     INSERT INTO TBL_DECEASED_VIDEO (id_deceased, id_metadata, video_link)
#                     VALUES (%s, %s, %s)
#                 """, [id, metadata_id, uploaded_video_url])

#                 # - Insertar en TBL_VIDEO
#                 cursor.execute("""
#                     INSERT INTO TBL_VIDEO (id_video, video_link, event_title, description)
#                     VALUES (%s, %s, %s, %s)
#                 """, [metadata_id, uploaded_video_url, event, desc])

#         # 7) Todo OK, devolvemos la entidad actualizada (puedes devolver el serializer o simplemente status 200)
#         return Response(serializer.data, status=status.HTTP_200_OK)

# api/views.py  (AppServer)

from datetime import datetime
import os
from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.core.files.storage import FileSystemStorage

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Deceased
from .serializers import DeceasedSerializer

# api/views.py  (AppServer)

from datetime import datetime
import os

from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.core.files.storage import FileSystemStorage

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Deceased  # Asegúrate de que aquí esté correctamente importado
from .serializers import DeceasedSerializer  # Lo seguiremos usando solo para validación

### EditFamilyMemberView (AppServer) con UPDATE manual

# api/views.py  (AppServer)

from datetime import datetime
import os

from django.shortcuts import get_object_or_404
from django.db import connection, transaction
from django.core.files.storage import FileSystemStorage

from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from .models import Deceased
from .serializers import DeceasedSerializer  # Solo para validación si se necesita


class EditFamilyMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @transaction.atomic
    def put(self, request, id):
        # 1) Obtener el objeto o 404
        miembro = get_object_or_404(Deceased, id_deceased=id)
        user = request.user

        # 2) Verificar permiso en TBL_USER_DECEASED
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT has_permission 
                  FROM TBL_USER_DECEASED
                 WHERE id_user = %s AND id_deceased = %s
            """, [user.id_user, id])
            if not cursor.fetchone():
                return Response({"detail": "No permission to edit this deceased."},
                                status=status.HTTP_403_FORBIDDEN)

        # 3) Extraer y validar manualmente los campos principales
        data = request.data  # JSON enviado por AppWeb

        name_str         = data.get('name', None)
        date_birth_str   = data.get('date_birth', None)
        date_death_str   = data.get('date_death', None)
        description_str  = data.get('description', None)
        burial_place_str = data.get('burial_place', None)

        # Validaciones básicas
        if name_str is not None and len(name_str) > 100:
            return Response({"name": "Máximo 100 caracteres."}, status=status.HTTP_400_BAD_REQUEST)
        if description_str is not None and len(description_str) > 100:
            return Response({"description": "Máximo 100 caracteres."}, status=status.HTTP_400_BAD_REQUEST)

        # Parsear fechas YYYY-MM-DD
        date_birth_val = None
        if date_birth_str:
            try:
                date_birth_val = datetime.strptime(date_birth_str, '%Y-%m-%d')
            except ValueError:
                return Response({"date_birth": "Formato inválido, debe ser 'YYYY-MM-DD'"},
                                status=status.HTTP_400_BAD_REQUEST)

        date_death_val = None
        if date_death_str:
            try:
                date_death_val = datetime.strptime(date_death_str, '%Y-%m-%d')
            except ValueError:
                return Response({"date_death": "Formato inválido, debe ser 'YYYY-MM-DD'"},
                                status=status.HTTP_400_BAD_REQUEST)

        # 4) Construir dinámicamente el UPDATE SQL para no sobrescribir con NULL
        campos = []
        valores = []

        if name_str is not None:
            campos.append("name = %s")
            valores.append(name_str)
        if date_birth_val is not None:
            campos.append("date_birth = %s")
            valores.append(date_birth_val)
        if date_death_val is not None:
            campos.append("date_death = %s")
            valores.append(date_death_val)
        if description_str is not None:
            campos.append("description = %s")
            valores.append(description_str)
        if burial_place_str is not None:
            campos.append("burial_place = %s")
            valores.append(burial_place_str)

        if campos:
            set_clause = ", ".join(campos)
            valores.append(id)
            sql = f"UPDATE TBL_DECEASED SET {set_clause} WHERE id_deceased = %s"
            with connection.cursor() as cursor:
                cursor.execute(sql, valores)

        # Verificar en consola
        miembro.refresh_from_db()
        # print("DEBUG — AppServer: tras UPDATE, miembro.name        =", miembro.name)
        # print("DEBUG — AppServer: tras UPDATE, miembro.date_birth  =", miembro.date_birth)
        # print("DEBUG — AppServer: tras UPDATE, miembro.date_death  =", miembro.date_death)
        # print("DEBUG — AppServer: tras UPDATE, miembro.description =", miembro.description)
        # print("DEBUG — AppServer: tras UPDATE, miembro.burial_place=", miembro.burial_place)

        # 5) Manejo de relaciones
        if hasattr(data, 'getlist'):
            related_ids = data.getlist('related_deceased[]')
            relationship_types = data.getlist('relationship_type[]')
            deleted_relation_ids = data.getlist('deleted_relation_ids[]')
        else:
            related_ids = data.get('related_deceased', [])
            relationship_types = data.get('relationship_type', [])
            deleted_relation_ids = data.get('deleted_relation_ids', [])

        with connection.cursor() as cursor:
            for del_id in deleted_relation_ids:
                cursor.execute("""
                    DELETE FROM TBL_RELATION
                     WHERE id_deceased = %s AND id_parent = %s
                """, [id, del_id])
            cursor.execute("SELECT id_parent FROM TBL_RELATION WHERE id_deceased = %s", [id])
            existing_ids = set(row[0] for row in cursor.fetchall())
            for rid, rtype in zip(related_ids, relationship_types):
                if rid and rtype and int(rid) not in existing_ids:
                    cursor.execute("""
                        INSERT INTO TBL_RELATION (id_deceased, id_parent, relationship)
                        VALUES (%s, %s, %s)
                    """, [id, int(rid), rtype])

        # 6) Manejo de imágenes
        if hasattr(data, 'getlist'):
            delete_image_ids   = data.getlist('delete_image_ids[]')
            existing_image_ids = data.getlist('existing_image_id[]')
        else:
            delete_image_ids   = data.get('delete_image_ids', [])
            existing_image_ids = data.get('existing_image_id', [])

        with connection.cursor() as cursor:
            for del_id in delete_image_ids:
                cursor.execute("DELETE FROM TBL_DECEASED_IMAGE WHERE id_metadata = %s", [del_id])
                cursor.execute("DELETE FROM TBL_IMAGE WHERE id_image = %s", [del_id])
            for idx, img_id in enumerate(existing_image_ids):
                event = data.get(f'existing_image_event_{idx}', '')
                desc  = data.get(f'existing_image_desc_{idx}', '')
                cursor.execute("""
                    UPDATE TBL_IMAGE
                       SET event_title = %s, description = %s
                     WHERE id_image = %s
                """, [event, desc, img_id])
            fs_imagenes = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'images'))
            for idx, image_file in enumerate(request.FILES.getlist('images')):
                filename = fs_imagenes.save(image_file.name, image_file)
                url = fs_imagenes.url(filename)
                event = data.get(f'image_event_{idx}', '')
                desc  = data.get(f'image_desc_{idx}', '')
                cursor.execute("INSERT INTO TBL_IMAGE_METADATA (date_created, coordinates) VALUES (%s, %s)", [datetime.now(), ""])
                metadata_id = cursor.lastrowid
                cursor.execute("INSERT INTO TBL_DECEASED_IMAGE (id_deceased, id_metadata, image_link) VALUES (%s, %s, %s)", [id, metadata_id, url])
                cursor.execute("INSERT INTO TBL_IMAGE (id_image, image_link, event_title, description) VALUES (%s, %s, %s, %s)", [metadata_id, url, event, desc])

        # 7) Manejo de vídeos (análogo)
        if hasattr(data, 'getlist'):
            delete_video_ids   = data.getlist('delete_video_ids[]')
            existing_video_ids = data.getlist('existing_video_id[]')
        else:
            delete_video_ids   = data.get('delete_video_ids', [])
            existing_video_ids = data.get('existing_video_id', [])

        with connection.cursor() as cursor:
            for del_id in delete_video_ids:
                cursor.execute("DELETE FROM TBL_DECEASED_VIDEO WHERE id_metadata = %s", [del_id])
                cursor.execute("DELETE FROM TBL_VIDEO WHERE id_video = %s", [del_id])
            for idx, vid_id in enumerate(existing_video_ids):
                event = data.get(f'existing_video_event_{idx}', '')
                desc  = data.get(f'existing_video_desc_{idx}', '')
                cursor.execute("""
                    UPDATE TBL_VIDEO
                       SET event_title = %s, description = %s
                     WHERE id_video = %s
                """, [event, desc, vid_id])
            fs_videos = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'videos'))
            for idx, video_file in enumerate(request.FILES.getlist('videos')):
                filename = fs_videos.save(video_file.name, video_file)
                url = fs_videos.url(filename)
                event = data.get(f'video_event_{idx}', '')
                desc  = data.get(f'video_desc_{idx}', '')
                cursor.execute("INSERT INTO TBL_VIDEO_METADATA (date_created, coordinates) VALUES (%s, %s)", [datetime.now(), ""])
                metadata_id = cursor.lastrowid
                cursor.execute("INSERT INTO TBL_DECEASED_VIDEO (id_deceased, id_metadata, video_link) VALUES (%s, %s, %s)", [id, metadata_id, url])
                cursor.execute("INSERT INTO TBL_VIDEO (id_video, video_link, event_title, description) VALUES (%s, %s, %s, %s)", [metadata_id, url, event, desc])

        # 8) Devolver JSON con datos actualizados
        return Response({
            "id_deceased": miembro.id_deceased,
            "name": miembro.name,
            "date_birth": miembro.date_birth.isoformat() if miembro.date_birth else None,
            "date_death": miembro.date_death.isoformat() if miembro.date_death else None,
            "description": miembro.description,
            "burial_place": miembro.burial_place,
            "visualization_state": miembro.visualization_state,
            "visualization_code": miembro.visualization_code,
        }, status=status.HTTP_200_OK)



class DeleteFamilyMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def delete(self, request, id):
        try:
            miembro = Deceased.objects.get(id_deceased=id)
        except Deceased.DoesNotExist:
            return Response({"detail": "Deceased not found."}, status=status.HTTP_404_NOT_FOUND)

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM TBL_RELATION WHERE id_deceased = %s OR id_parent = %s", [id, id])

            cursor.execute("SELECT id_metadata FROM TBL_DECEASED_VIDEO WHERE id_deceased = %s", [id])
            video_metadata_ids = [row[0] for row in cursor.fetchall()]
            cursor.execute("DELETE FROM TBL_DECEASED_VIDEO WHERE id_deceased = %s", [id])
            for meta_id in video_metadata_ids:
                cursor.execute("DELETE FROM TBL_VIDEO WHERE id_video = %s", [meta_id])
                cursor.execute("DELETE FROM TBL_VIDEO_METADATA WHERE id_metadata = %s", [meta_id])

            cursor.execute("SELECT id_metadata FROM TBL_DECEASED_IMAGE WHERE id_deceased = %s", [id])
            image_metadata_ids = [row[0] for row in cursor.fetchall()]
            cursor.execute("DELETE FROM TBL_DECEASED_IMAGE WHERE id_deceased = %s", [id])
            for meta_id in image_metadata_ids:
                cursor.execute("DELETE FROM TBL_IMAGE WHERE id_image = %s", [meta_id])
                cursor.execute("DELETE FROM TBL_IMAGE_METADATA WHERE id_metadata = %s", [meta_id])

            cursor.execute("DELETE FROM TBL_USER_DECEASED WHERE id_deceased = %s", [id])
            cursor.execute("DELETE FROM TBL_REQUEST WHERE id_deceased = %s", [id])
            cursor.execute("DELETE FROM TBL_DECEASED WHERE id_deceased = %s", [id])

        return Response({"detail": "Deceased deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Puedes crear más vistas para request_access, approve_request, notifications, etc. siguiendo el mismo patrón de APIView con JSON y serializers.

class RequestAccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, id_deceased):
        user = request.user

        with connection.cursor() as cursor:
            # Verificar si ya hay solicitud pendiente del mismo usuario y fallecido
            cursor.execute("""
                SELECT COUNT(*) FROM TBL_REQUEST
                WHERE id_issuer = %s AND id_deceased = %s AND request_status = 'pending'
            """, [user.id_user, id_deceased])
            if cursor.fetchone()[0] > 0:
                return Response({"detail": "You already have a pending request for this deceased."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Obtener creador (usuario con permiso) del fallecido
            cursor.execute("""
                SELECT id_user FROM TBL_USER_DECEASED
                WHERE id_deceased = %s AND has_permission = 1 LIMIT 1
            """, [id_deceased])
            creator = cursor.fetchone()
            if not creator:
                return Response({"detail": "No creator with permission found for this deceased."},
                                status=status.HTTP_404_NOT_FOUND)
            creator_id = creator[0]

            # Insertar solicitud
            cursor.execute("""
                INSERT INTO TBL_REQUEST (id_issuer, id_receiver, id_deceased, creation_date, request_type, request_status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [user.id_user, creator_id, id_deceased, timezone.now(), 'view', 'pending'])
            request_id = cursor.lastrowid

            # Insertar notificación al creador
            cursor.execute("""
                INSERT INTO TBL_NOTIFICATION (id_sender, id_receiver, message, creation_date, is_read)
                VALUES (%s, %s, %s, %s, %s)
            """, [user.id_user, creator_id, f"{user.name} has requested access. Request #{request_id}", timezone.now(), False])

        return Response({"detail": "Access request created successfully."}, status=status.HTTP_201_CREATED)


class ApproveRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, request_id, action):
        if action not in ['approved', 'rejected']:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        approver = request.user

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_issuer, id_deceased FROM TBL_REQUEST WHERE id_request = %s
            """, [request_id])
            row = cursor.fetchone()
            if not row:
                return Response({"detail": "Request not found."}, status=status.HTTP_404_NOT_FOUND)

            requester_id, deceased_id = row

            cursor.execute("""
                UPDATE TBL_REQUEST SET request_status = %s WHERE id_request = %s
            """, [action, request_id])

            if action == 'approved':
                cursor.execute("""
                    DELETE FROM TBL_USER_DECEASED WHERE id_user = %s AND id_deceased = %s
                """, [requester_id, deceased_id])

                cursor.execute("""
                    INSERT INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                    VALUES (%s, %s, %s, %s)
                """, [requester_id, deceased_id, timezone.now(), False])

                message = f"✅ Your request to access memory ID {deceased_id} was approved."
            else:
                message = f"❌ Your request to access memory ID {deceased_id} was rejected."

            cursor.execute("""
                INSERT INTO TBL_NOTIFICATION (id_sender, id_receiver, message, creation_date, is_read)
                VALUES (%s, %s, %s, %s, %s)
            """, [approver.id_user, requester_id, message, timezone.now(), False])

            # MARCAR LA NOTIFICACIÓN ORIGINAL COMO LEÍDA
            cursor.execute("""
                UPDATE TBL_NOTIFICATION SET is_read = 1
                WHERE id_receiver = %s AND message LIKE %s
            """, [approver.id_user, f"%Request #{request_id}%"])

        return Response({"detail": f"Request {action} successfully."}, status=status.HTTP_200_OK)



class NotificationsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_notification, id_sender, message, is_read, creation_date
                FROM TBL_NOTIFICATION
                WHERE id_receiver = %s
                ORDER BY creation_date DESC
            """, [user.id_user])

            columns = [col[0] for col in cursor.description]
            for row in cursor.fetchall():
                notifications.append(dict(zip(columns, row)))

        return Response(notifications)



class MarkNotificationReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, notification_id):
        user = request.user
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE TBL_NOTIFICATION SET is_read = 1
                WHERE id_notification = %s AND id_receiver = %s
            """, [notification_id, user.id_user])
            if cursor.rowcount == 0:
                return Response({"detail": "Notification not found or no permission."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "Notification marked as read."}, status=status.HTTP_200_OK)


class HandleNotificationActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, notification_id, action):
        user = request.user

        if action not in ['accept', 'decline', 'read']:
            return Response({"detail": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id_sender, message FROM TBL_NOTIFICATION
                WHERE id_notification = %s AND id_receiver = %s
            """, [notification_id, user.id_user])
            notif = cursor.fetchone()

            if not notif:
                return Response({"detail": "Notification not found or no permission."}, status=status.HTTP_404_NOT_FOUND)

            sender_id, message = notif

            # Caso: solicitud de acceso con ID de request
            match_request = re.search(r"Request #(\d+)", message)
            if match_request:
                request_id = int(match_request.group(1))

                cursor.execute("SELECT id_deceased FROM TBL_REQUEST WHERE id_request = %s", [request_id])
                row = cursor.fetchone()
                if not row:
                    return Response({"detail": "Request data not found."}, status=status.HTTP_404_NOT_FOUND)
                id_deceased = row[0]

                if action == 'accept':
                    cursor.execute("""
                        INSERT IGNORE INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                        VALUES (%s, %s, %s, %s)
                    """, [user.id_user, id_deceased, timezone.now(), False])

            # 🔥 Nuevo caso: notificación de memoria compartida
            match_shared = re.search(r"shared memory ID (\d+)", message)
            if match_shared:
                id_deceased = int(match_shared.group(1))

                if action == 'accept':
                    cursor.execute("""
                        INSERT IGNORE INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                        VALUES (%s, %s, %s, %s)
                    """, [user.id_user, id_deceased, timezone.now(), False])

            # Marcar la notificación como leída siempre
            cursor.execute("""
                UPDATE TBL_NOTIFICATION SET is_read = 1 WHERE id_notification = %s
            """, [notification_id])

        return Response({"detail": f"Notification action '{action}' handled."}, status=status.HTTP_200_OK)


class DeceasedSearchView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = []
        if query:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id_deceased, name FROM TBL_DECEASED
                    WHERE LOWER(name) LIKE %s
                    LIMIT 10
                """, [f"%{query.lower()}%"])
                rows = cursor.fetchall()
                for row in rows:
                    results.append({'id': row[0], 'name': row[1]})
        return Response({'results': results})


class UploadImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        image_file = request.FILES.get('image_file')
        event_title = request.data.get('event_title', '')
        description = request.data.get('description', '')
        id_deceased = request.data.get('id_deceased')

        if not image_file or not id_deceased:
            return Response({'error': 'Missing image file or deceased ID'}, status=status.HTTP_400_BAD_REQUEST)

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'images'))
        filename = fs.save(image_file.name, image_file)
        uploaded_file_url = fs.url(filename)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TBL_IMAGE_METADATA (date_created, coordinates)
                VALUES (%s, %s)
            """, [timezone.now(), ''])
            metadata_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO TBL_DECEASED_IMAGE (id_deceased, id_metadata, image_link)
                VALUES (%s, %s, %s)
            """, [id_deceased, metadata_id, uploaded_file_url])

            cursor.execute("""
                INSERT INTO TBL_IMAGE (id_image, image_link, event_title, description)
                VALUES (%s, %s, %s, %s)
            """, [metadata_id, uploaded_file_url, event_title, description])

        return Response({
            'message': 'Image uploaded successfully',
            'image_link': uploaded_file_url,
            'id_metadata': metadata_id,
        }, status=status.HTTP_201_CREATED)

class UploadVideoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        video_file = request.FILES.get('video_file')
        event_title = request.data.get('event_title', '')
        description = request.data.get('description', '')
        id_deceased = request.data.get('id_deceased')

        if not video_file or not id_deceased:
            return Response({'error': 'Missing video file or deceased ID'}, status=status.HTTP_400_BAD_REQUEST)

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads', 'videos'))
        filename = fs.save(video_file.name, video_file)
        uploaded_file_url = fs.url(filename)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO TBL_VIDEO_METADATA (date_created, coordinates)
                VALUES (%s, %s)
            """, [timezone.now(), ''])
            metadata_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO TBL_DECEASED_VIDEO (id_deceased, id_metadata, video_link)
                VALUES (%s, %s, %s)
            """, [id_deceased, metadata_id, uploaded_file_url])

            cursor.execute("""
                INSERT INTO TBL_VIDEO (id_video, video_link, event_title, description)
                VALUES (%s, %s, %s, %s)
            """, [metadata_id, uploaded_file_url, event_title, description])

        return Response({
            'message': 'Video uploaded successfully',
            'video_link': uploaded_file_url,
            'id_metadata': metadata_id,
        }, status=status.HTTP_201_CREATED)