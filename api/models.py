from django.db import models

# class User(models.Model):
#     id_user = models.BigAutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     email = models.CharField(max_length=100)
#     password = models.CharField(max_length=250)  # En producción, usa campos de contraseña seguros

#     class Meta:
#         db_table = 'TBL_USER'  # Esto indica a Django que use tu tabla existente
#         managed = False  # Indica a Django que no gestione esta tabla (ya existe)

class User(models.Model):
    id_user = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=250, blank=True, null=True)  # Igual que appWeb

    class Meta:
        db_table = 'TBL_USER'
        managed = False

# class Deceased(models.Model):
#     id_deceased = models.BigAutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     date_birth = models.DateTimeField()
#     date_death = models.DateTimeField()
#     description = models.CharField(max_length=100)
#     burial_place = models.CharField(max_length=100)
#     visualization_state = models.BooleanField()
#     visualization_code = models.CharField(max_length=100)

#     class Meta:
#         db_table = 'TBL_DECEASED'
#         managed = False

class Deceased(models.Model):
    id_deceased = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    date_birth = models.DateTimeField(null=True, blank=True)  # ← CAMBIO
    date_death = models.DateTimeField(null=True, blank=True)  # ← CAMBIO
    description = models.CharField(max_length=100, null=True, blank=True)  # ← CAMBIO
    burial_place = models.CharField(max_length=100, null=True, blank=True)  # ← CAMBIO
    visualization_state = models.BooleanField(default=True)  # ← CAMBIO
    visualization_code = models.CharField(max_length=100, null=True, blank=True)  # ← CAMBIO

    class Meta:
        db_table = 'TBL_DECEASED'
        managed = False

# class Video(models.Model):
#     id_video = models.BigAutoField(primary_key=True)
#     video_link = models.CharField(max_length=1000)
#     event_title = models.CharField(max_length=100)
#     description = models.CharField(max_length=100)

#     class Meta:
#         db_table = 'TBL_VIDEO'
#         managed = False

class Video(models.Model):
    id_video = models.BigAutoField(primary_key=True)
    video_link = models.CharField(max_length=1000)
    event_title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)  # ← CAMBIO para igualar con appWeb

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
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    id_metadata = models.ForeignKey(VideoMetadata, on_delete=models.CASCADE, db_column='id_metadata')
    video_link = models.CharField(max_length=1000)

    class Meta:
        db_table = 'TBL_DECEASED_VIDEO'
        managed = False
        unique_together = (('id_deceased', 'id_metadata'),)

# class Image(models.Model):
#     id_image = models.BigAutoField(primary_key=True)
#     image_link = models.CharField(max_length=1000)
#     event_title = models.CharField(max_length=100)
#     description = models.CharField(max_length=100)

#     class Meta:
#         db_table = 'TBL_IMAGE'
#         managed = False

class Image(models.Model):
    id_image = models.BigAutoField(primary_key=True)
    image_link = models.CharField(max_length=1000)
    event_title = models.CharField(max_length=100)
    description = models.CharField(max_length=255)  # ← CAMBIO para igualar con appWeb

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
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    id_metadata = models.ForeignKey(ImageMetadata, on_delete=models.CASCADE, db_column='id_metadata')
    image_link = models.CharField(max_length=1000)

    class Meta:
        db_table = 'TBL_DECEASED_IMAGE'
        managed = False
        unique_together = (('id_deceased', 'id_metadata'),)

class RelationshipType(models.Model):
    relationship = models.CharField(primary_key=True, max_length=100)

    class Meta:
        db_table = 'TBL_RELATIONSHIP_TYPE'
        managed = False

class Relation(models.Model):
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, related_name='child', db_column='id_deceased')
    id_parent = models.ForeignKey(Deceased, on_delete=models.CASCADE, related_name='parent', db_column='id_parent')
    relationship = models.ForeignKey(RelationshipType, on_delete=models.CASCADE, db_column='relationship')

    class Meta:
        db_table = 'TBL_RELATION'
        managed = False
        unique_together = (('id_deceased', 'id_parent'),)

class UserDeceased(models.Model):
    id_user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='id_user')
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    date_relation = models.DateTimeField()
    has_permission = models.BooleanField()

    class Meta:
        db_table = 'TBL_USER_DECEASED'
        managed = False
        unique_together = (('id_user', 'id_deceased'),)

class Request(models.Model):
    id_request = models.BigAutoField(primary_key=True)
    id_issuer = models.ForeignKey('User', on_delete=models.CASCADE, related_name='issued_requests', db_column='id_issuer')
    id_receiver = models.ForeignKey('User', on_delete=models.CASCADE, related_name='received_requests', db_column='id_receiver')
    id_deceased = models.ForeignKey(Deceased, on_delete=models.CASCADE, db_column='id_deceased')
    creation_date = models.DateField()
    request_type = models.CharField(max_length=50)
    request_status = models.CharField(max_length=50)

    class Meta:
        db_table = 'TBL_REQUEST'
        managed = False

class Notification(models.Model):
    id_notification = models.BigAutoField(primary_key=True)
    id_sender = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_notifications', db_column='id_sender')
    id_receiver = models.ForeignKey('User', on_delete=models.CASCADE, related_name='received_notifications', db_column='id_receiver')
    message = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    creation_date = models.DateTimeField()

    class Meta:
        db_table = 'TBL_NOTIFICATION'
        managed = False

class QR(models.Model):
    id_qr = models.BigAutoField(primary_key=True)
    id_user = models.ForeignKey('User', on_delete=models.CASCADE, db_column='id_user')
    qr_code = models.BigIntegerField(unique=True)
    visualization_status = models.CharField(max_length=50)
    generation_date = models.DateTimeField()

    class Meta:
        db_table = 'TBL_QR'
        managed = False