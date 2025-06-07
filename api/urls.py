from django.urls import path
from . import views
from .views import (
    UserIdByQrCodeView, 
    DeceasedByUserView, 
    ImagesByDeceasedView, 
    VideosByDeceasedView, 
    RelationsByDeceasedView, 
    DashboardView, 
    AddFamilyMemberView, 
    FamilyMemberListView, 
    ShareFamilyMemberView, 
    EditFamilyMemberView, 
    DeleteFamilyMemberView, 
    RequestAccessView, 
    ApproveRequestView, 
    NotificationsListView, 
    MarkNotificationReadView, 
    HandleNotificationActionView, 
    OAuth2PasswordLoginView, 
    DeceasedSearchView, 
    UploadImageView, 
    UploadVideoView, 
    UserByEmailView
)

urlpatterns = [
    # User
    path('users/', views.UserListCreate.as_view(), name="user_list_create"),
    path('users/<int:pk>/', views.UserRetrieveUpdateDestroy.as_view(), name="user_detail"),
    path('auth/login/', OAuth2PasswordLoginView.as_view(), name='oauth2_password_login'),
    
    # Deceased
    path('deceased/', views.DeceasedListCreate.as_view(), name="deceased_list_create"),
    path('deceased/<int:pk>/', views.DeceasedRetrieveUpdateDestroy.as_view(), name="deceased_detail"),
    
    # Video
    path('videos/', views.VideoListCreate.as_view(), name="video_list_create"),
    path('videos/<int:pk>/', views.VideoRetrieveUpdateDestroy.as_view(), name="video_detail"),
    
    # Video Metadata
    path('video-metadata/', views.VideoMetadataListCreate.as_view(), name="video_metadata_list_create"),
    path('video-metadata/<int:pk>/', views.VideoMetadataRetrieveUpdateDestroy.as_view(), name="video_metadata_detail"),
    
    # Deceased-Video (Tabla puente)
    path('deceased-videos/', views.DeceasedVideoListCreate.as_view(), name="deceased_video_list_create"),
    path('deceased-videos/<int:pk>/', views.DeceasedVideoRetrieveUpdateDestroy.as_view(), name="deceased_video_detail"),
    
    # Image
    path('images/', views.ImageListCreate.as_view(), name="image_list_create"),
    path('images/<int:pk>/', views.ImageRetrieveUpdateDestroy.as_view(), name="image_detail"),
    
    # Image Metadata
    path('image-metadata/', views.ImageMetadataListCreate.as_view(), name="image_metadata_list_create"),
    path('image-metadata/<int:pk>/', views.ImageMetadataRetrieveUpdateDestroy.as_view(), name="image_metadata_detail"),
    
    # Deceased-Image (Tabla puente)
    path('deceased-images/', views.DeceasedImageListCreate.as_view(), name="deceased_image_list_create"),
    path('deceased-images/<int:pk>/', views.DeceasedImageRetrieveUpdateDestroy.as_view(), name="deceased_image_detail"),
    
    # Relationships
    path('relationship-types/', views.RelationshipTypeListCreate.as_view(), name="relationship_type_list_create"),
    path('relationship-types/<str:pk>/', views.RelationshipTypeRetrieveUpdateDestroy.as_view(), name="relationship_type_detail"),
    path('relations/', views.RelationListCreate.as_view(), name="relation_list_create"),
    path('relations/<int:pk>/', views.RelationRetrieveUpdateDestroy.as_view(), name="relation_detail"),
    
    # User-Deceased
    path('user-deceased/', views.UserDeceasedListCreate.as_view(), name="user_deceased_list_create"),
    path('user-deceased/<int:pk>/', views.UserDeceasedRetrieveUpdateDestroy.as_view(), name="user_deceased_detail"),
    
    # Requests
    path('requests/', views.RequestListCreate.as_view(), name="request_list_create"),
    path('requests/<int:pk>/', views.RequestRetrieveUpdateDestroy.as_view(), name="request_detail"),
    
    # Notifications
    path('notifications/', views.NotificationListCreate.as_view(), name="notification_list_create"),
    path('notifications/<int:pk>/', views.NotificationRetrieveUpdateDestroy.as_view(), name="notification_detail"),
    
    # QR Codes
    path('qr-codes/', views.QRListCreate.as_view(), name="qr_list_create"),
    path('qr-codes/<int:pk>/', views.QRRetrieveUpdateDestroy.as_view(), name="qr_detail"),

    # Google AUTH
    path('auth/google/', views.google_login, name='google_login'),

    # APP VR
    path('vr/user-id-by-qr/<int:qr_code>/', UserIdByQrCodeView.as_view(), name='user_id_by_qr'),
    path('vr/deceased-by-user/<int:user_id>/', DeceasedByUserView.as_view(), name='deceased_by_user'),
    path('vr/images-by-deceased/<int:deceased_id>/', ImagesByDeceasedView.as_view(), name='images_by_deceased'),
    path('vr/videos-by-deceased/<int:deceased_id>/', VideosByDeceasedView.as_view(), name='videos_by_deceased'),
    path('vr/relations-by-deceased/<int:deceased_id>/', RelationsByDeceasedView.as_view(), name='relations_by_deceased'),

    # APP WEB
    path('appweb/dashboard/', DashboardView.as_view(), name='appweb_dashboard'),
    path('appweb/family-members/', FamilyMemberListView.as_view(), name='appweb_family_member_list'),
    path('appweb/family-members/add/', AddFamilyMemberView.as_view(), name='appweb_add_family_member'),
    path('appweb/family-members/<int:id>/share/', ShareFamilyMemberView.as_view(), name='appweb_share_family_member'),
    path('appweb/family-members/<int:id>/edit/', EditFamilyMemberView.as_view(), name='appweb_edit_family_member'),
    path('appweb/family-members/<int:id>/delete/', DeleteFamilyMemberView.as_view(), name='appweb_delete_family_member'),

    path('appweb/request-access/<int:id_deceased>/', RequestAccessView.as_view(), name='appweb_request_access'),
    path('appweb/approve-request/<int:request_id>/<str:action>/', ApproveRequestView.as_view(), name='appweb_approve_request'),

    path('appweb/notifications/', NotificationsListView.as_view(), name='appweb_notifications'),
    path('appweb/notifications/read/<int:notification_id>/', MarkNotificationReadView.as_view(), name='appweb_mark_notification_read'),
    path('appweb/notification-action/<int:notification_id>/<str:action>/', HandleNotificationActionView.as_view(), name='appweb_handle_notification_action'),

    # Búsqueda AJAX
    path('deceased/search/', DeceasedSearchView.as_view(), name='deceased_search'),

    # Upload Image & Video
    path('upload/image/', UploadImageView.as_view(), name='upload_image'),
    path('upload/video/', UploadVideoView.as_view(), name='upload_video'),

    # Email Filter
    path('users/by-email/', UserByEmailView.as_view(), name='user_by_email'),
]
