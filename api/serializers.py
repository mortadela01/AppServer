from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'  # No incluyas la contraseña en el serializer (sí la incluyo jaja)

class DeceasedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deceased
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Video
        fields = '__all__'

class VideoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMetadata
        fields = '__all__'

class DeceasedVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeceasedVideo
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class ImageMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMetadata
        fields = '__all__'

class DeceasedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeceasedImage
        fields = '__all__'

class RelationshipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationshipType
        fields = '__all__'

class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = '__all__'

class UserDeceasedSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDeceased
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = '__all__'