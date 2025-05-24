
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


class AddFamilyMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        data = request.data.copy()

        # Guardar información básica de fallecido
        serializer = DeceasedSerializer(data=data)
        if serializer.is_valid():
            new_deceased = serializer.save()

            # Guardar relaciones familiares
            related = data.get('related_deceased', [])
            relationship_types = data.get('relationship_type', [])
            if related and relationship_types and len(related) == len(relationship_types):
                with connection.cursor() as cursor:
                    for related_id, rel_type in zip(related, relationship_types):
                        cursor.execute("""
                            INSERT INTO TBL_RELATION (id_deceased, id_parent, relationship)
                            VALUES (%s, %s, %s)
                        """, [new_deceased.id_deceased, int(related_id), rel_type])

            # Crear relación usuario-fallecido con permiso
            user = request.user
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                    VALUES (%s, %s, %s, %s)
                """, [user.id_user, new_deceased.id_deceased, timezone.now(), 1])

            # NOTA: Aquí no se manejan archivos multimedia (imágenes/videos) porque esa lógica es más compleja vía API
            # Se recomienda crear endpoints separados para upload de imágenes y videos vinculados.

            return Response(DeceasedSerializer(new_deceased).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FamilyMemberListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        miembros = []
        permisos = []
        otros_deceased = []

        with connection.cursor() as cursor:
            # Obtener fallecidos relacionados al usuario
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
                miembros.append(miembro)

            # Obtener otros fallecidos no relacionados
            cursor.execute("""
                SELECT * FROM TBL_DECEASED
                WHERE id_deceased NOT IN (
                    SELECT id_deceased FROM TBL_USER_DECEASED WHERE id_user = %s
                )
            """, [user.id_user])
            otros_deceased = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

        return Response({
            "miembros": miembros,
            "permisos": permisos,
            "otros_deceased": otros_deceased,
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


class EditFamilyMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def put(self, request, id):
        try:
            miembro = Deceased.objects.get(id_deceased=id)
        except Deceased.DoesNotExist:
            return Response({"detail": "Deceased not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT has_permission FROM TBL_USER_DECEASED
                WHERE id_user = %s AND id_deceased = %s
            """, [user.id_user, id])
            perm = cursor.fetchone()
            if not perm:
                return Response({"detail": "No permission to edit this deceased."}, status=status.HTTP_403_FORBIDDEN)

        serializer = DeceasedSerializer(miembro, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            related_ids = request.data.get('related_deceased', [])
            relationship_types = request.data.get('relationship_type', [])
            deleted_relation_ids = request.data.get('deleted_relation_ids', [])

            with connection.cursor() as cursor:
                # Delete relations marked for removal
                for del_id in deleted_relation_ids:
                    cursor.execute("""
                        DELETE FROM TBL_RELATION WHERE id_deceased = %s AND id_parent = %s
                    """, [id, del_id])

                # Insert new relations if not exist
                cursor.execute("SELECT id_parent FROM TBL_RELATION WHERE id_deceased = %s", [id])
                existing_ids = set(row[0] for row in cursor.fetchall())
                for related_id, rel_type in zip(related_ids, relationship_types):
                    if related_id and rel_type and int(related_id) not in existing_ids:
                        cursor.execute("""
                            INSERT INTO TBL_RELATION (id_deceased, id_parent, relationship)
                            VALUES (%s, %s, %s)
                        """, [id, int(related_id), rel_type])

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        # action esperado: "approved" o "rejected"
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

            # Actualizar estado de la solicitud
            cursor.execute("""
                UPDATE TBL_REQUEST SET request_status = %s WHERE id_request = %s
            """, [action, request_id])

            if action == 'approved':
                # Borrar permisos duplicados si existen
                cursor.execute("""
                    DELETE FROM TBL_USER_DECEASED WHERE id_user = %s AND id_deceased = %s
                """, [requester_id, deceased_id])

                # Insertar permiso con has_permission=0 (solo vista)
                cursor.execute("""
                    INSERT INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                    VALUES (%s, %s, %s, %s)
                """, [requester_id, deceased_id, timezone.now(), False])

                message = f"✅ Your request to access memory ID {deceased_id} was approved."
            else:
                message = f"❌ Your request to access memory ID {deceased_id} was rejected."

            # Insertar notificación al solicitante
            cursor.execute("""
                INSERT INTO TBL_NOTIFICATION (id_sender, id_receiver, message, creation_date, is_read)
                VALUES (%s, %s, %s, %s, %s)
            """, [approver.id_user, requester_id, message, timezone.now(), False])

        return Response({"detail": f"Request {action} successfully."}, status=status.HTTP_200_OK)


class NotificationsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = []
        with connection.cursor() as cursor:
            # Marcar todas como leídas (opcional, o usar endpoint separado)
            cursor.execute("""
                UPDATE TBL_NOTIFICATION SET is_read = 1 WHERE id_receiver = %s
            """, [user.id_user])

            # Obtener todas las notificaciones del usuario
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
        # action puede ser: "accept", "decline", "read"
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
            match = re.search(r"memory ID (\d+)", message)

            if match:
                id_deceased = int(match.group(1))

                if action == 'accept':
                    # Insertar permiso con has_permission=0 (solo vista)
                    cursor.execute("""
                        INSERT IGNORE INTO TBL_USER_DECEASED (id_user, id_deceased, date_relation, has_permission)
                        VALUES (%s, %s, %s, %s)
                    """, [user.id_user, id_deceased, timezone.now(), False])
                # Para decline o read no se inserta permiso

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