from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser debe tener is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id_user = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=250)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='api_user_set',
        blank=True,
        help_text='Los grupos a los que pertenece el usuario.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='api_user_set',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        verbose_name='user permissions',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'TBL_USER'
        managed = False

    def __str__(self):
        return self.email

class Deceased(models.Model):
    id_deceased = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date_birth = models.DateField(null=True, blank=True)
    date_death = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    burial_place = models.CharField(max_length=100, null=True, blank=True)
    visualization_state = models.BooleanField(default=True)
    visualization_code = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'TBL_DECEASED'
        managed = False

    def __str__(self):
        return self.name


class Video(models.Model):
    id_video = models.BigAutoField(primary_key=True)
    video_link = models.CharField(max_length=1000)
    event_title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    class Meta:
        db_table = 'TBL_VIDEO'
        managed = False

class VideoMetadata(models.Model):
    id_metadata = models.BigAutoField(primary_key=True)
    date_created = models.DateTimeField()
    coordinates = models.CharField(max_length=100)

    class Meta:
        db_table = 'TBL_VIDEO_METADATA'
        managed = False

class DeceasedVideo(models.Model):
    id_deceased_video = models.BigAutoField(primary_key=True)
    id_video = models.ForeignKey(Video, on_delete=models.CASCADE, db_column='id_video')
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    id_metadata = models.ForeignKey(VideoMetadata, on_delete=models.CASCADE, db_column='id_metadata')
    video_link = models.CharField(max_length=1000)

    class Meta:
        db_table = 'TBL_DECEASED_VIDEO'
        managed = False
        unique_together = (('id_deceased', 'id_metadata'),)

class Image(models.Model):
    id_image = models.BigAutoField(primary_key=True)
    image_link = models.CharField(max_length=1000)
    event_title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    class Meta:
        db_table = 'TBL_IMAGE'
        managed = False

class ImageMetadata(models.Model):
    id_metadata = models.BigAutoField(primary_key=True)
    date_created = models.DateTimeField()
    coordinates = models.CharField(max_length=100)

    class Meta:
        db_table = 'TBL_IMAGE_METADATA'
        managed = False

class DeceasedImage(models.Model):
    id_deceased_image = models.BigAutoField(primary_key=True)
    id_image = models.ForeignKey(Image, on_delete=models.CASCADE, db_column='id_image')
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    id_metadata = models.ForeignKey(ImageMetadata, on_delete=models.CASCADE, db_column='id_metadata')
    image_link = models.CharField(max_length=1000)

    class Meta:
        db_table = 'TBL_DECEASED_IMAGE'
        managed = False
        unique_together = (('id_image', 'id_deceased', 'id_metadata'),)

class RelationshipType(models.Model):
    relationship = models.CharField(primary_key=True, max_length=100)

    class Meta:
        db_table = 'TBL_RELATIONSHIP_TYPE'
        managed = False

class Relation(models.Model):
    id_relation = models.BigAutoField(primary_key=True)
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, related_name='child', db_column='id_deceased')
    id_parent = models.ForeignKey(Deceased, on_delete=models.CASCADE, related_name='parent', db_column='id_parent')
    relationship = models.ForeignKey(RelationshipType, on_delete=models.CASCADE, db_column='relationship')

    class Meta:
        db_table = 'TBL_RELATION'
        managed = False
        unique_together = (('id_deceased', 'id_parent'),)

class UserDeceased(models.Model):
    id_user_deceased = models.BigAutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_user')
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    date_relation = models.DateTimeField()
    has_permission = models.BooleanField()

    class Meta:
        db_table = 'TBL_USER_DECEASED'
        managed = False
        unique_together = (('id_user', 'id_deceased'),)

class Request(models.Model):
    id_request = models.BigAutoField(primary_key=True)
    id_issuer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_requests', db_column='id_issuer')
    id_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests', db_column='id_receiver')
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    creation_date = models.DateField()
    request_type = models.CharField(max_length=50)
    request_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'TBL_REQUEST'
        managed = False

class Notification(models.Model):
    id_notification = models.BigAutoField(primary_key=True)
    id_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', db_column='id_sender')
    id_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications', db_column='id_receiver')
    message = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    creation_date = models.DateTimeField()

    class Meta:
        db_table = 'TBL_NOTIFICATION'
        managed = False

class QR(models.Model):
    id_qr = models.BigAutoField(primary_key=True)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='id_user')
    qr_code = models.BigIntegerField(unique=True)
    visualization_status = models.CharField(max_length=50)
    generation_date = models.DateTimeField()

    class Meta:
        db_table = 'TBL_QR'
        managed = False
