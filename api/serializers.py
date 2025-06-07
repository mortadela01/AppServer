from rest_framework import serializers
from .models import *
from .models import Deceased
import datetime

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'  # No incluyas la contraseña en el serializer (sí la incluyo jaja)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id_user', 'email', 'name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # aquí se hace el hash
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class DateOnlyField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, datetime.datetime):
            return value.date().isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        return None

    def to_internal_value(self, data):
        # Asumimos que data es string en formato 'YYYY-MM-DD'
        try:
            return datetime.datetime.strptime(data, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            raise serializers.ValidationError('Fecha inválida, debe ser YYYY-MM-DD')
        
class DeceasedSerializer(serializers.ModelSerializer):
    date_birth = DateOnlyField(required=False, allow_null=True)
    date_death = DateOnlyField(required=False, allow_null=True)

    class Meta:
        model = Deceased
        fields = [
            'id_deceased', 'name', 'date_birth', 'date_death',
            'description', 'burial_place', 'visualization_state',
            'visualization_code'
        ]

    def get_date_birth(self, obj):
        if obj.date_birth:
            # Puede ser datetime o date, convertimos a date
            return obj.date_birth.date() if hasattr(obj.date_birth, 'date') else obj.date_birth
        return None

    def get_date_death(self, obj):
        if obj.date_death:
            return obj.date_death.date() if hasattr(obj.date_death, 'date') else obj.date_death
        return None

    def to_internal_value(self, data):
        # Para que la validación en POST/PUT acepte strings ISO y convierta a date correctamente
        ret = super().to_internal_value(data)
        return ret


class VideoSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    description = serializers.CharField(allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = Video
        fields = ['event_title', 'description']

class VideoMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMetadata
        fields = '__all__'

class DeceasedVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeceasedVideo
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    event_title = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    description = serializers.CharField(allow_blank=True, required=False, allow_null=True)

    class Meta:
        model = Image
        fields = ['event_title', 'description']

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

