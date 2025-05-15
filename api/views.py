
from rest_framework import permissions
from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *

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