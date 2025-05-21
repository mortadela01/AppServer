from django.urls import path
from . import views  # Importa las vistas de tu app                                                                            ||||                                                                                                                           ||||                                   ||||                                                                           ||||
from .views import UserIdByQrCodeView, DeceasedByUserView, ImagesByDeceasedView, VideosByDeceasedView, RelationsByDeceasedView, DashboardView, AddFamilyMemberView, FamilyMemberListView, ShareFamilyMemberView, EditFamilyMemberView, DeleteFamilyMemberView, RequestAccessView, ApproveRequestView, NotificationsListView, MarkNotificationReadView, HandleNotificationActionView, OAuth2PasswordLoginView


urlpatterns = [
    # User
    path('users/', views.UserListCreate.as_view()),
    path('users/<int:pk>/', views.UserRetrieveUpdateDestroy.as_view()),
    path('auth/login/', OAuth2PasswordLoginView.as_view(), name='oauth2_password_login'),
    
    # Deceased
    path('deceased/', views.DeceasedListCreate.as_view()),
    path('deceased/<int:pk>/', views.DeceasedRetrieveUpdateDestroy.as_view()),
    
    # Video
    path('videos/', views.VideoListCreate.as_view()),
    path('videos/<int:pk>/', views.VideoRetrieveUpdateDestroy.as_view()),
    
    # Video Metadata
    path('video-metadata/', views.VideoMetadataListCreate.as_view()),
    path('video-metadata/<int:pk>/', views.VideoMetadataRetrieveUpdateDestroy.as_view()),
    
    # Deceased-Video (Tabla puente) #Tiene problemas por ser pk compuesta (solo funciona el create)
    path('deceased-videos/', views.DeceasedVideoListCreate.as_view()),
    path('deceased-videos/<int:pk>/', views.DeceasedVideoRetrieveUpdateDestroy.as_view()),
    
    # Image
    path('images/', views.ImageListCreate.as_view()),
    path('images/<int:pk>/', views.ImageRetrieveUpdateDestroy.as_view()),
    
    # Image Metadata
    path('image-metadata/', views.ImageMetadataListCreate.as_view()),
    path('image-metadata/<int:pk>/', views.ImageMetadataRetrieveUpdateDestroy.as_view()),
    
    # Deceased-Image (Tabla puente) #Tiene problemas por ser pk compuesta (solo funciona el create) 
    path('deceased-images/', views.DeceasedImageListCreate.as_view()),
    path('deceased-images/<int:pk>/', views.DeceasedImageRetrieveUpdateDestroy.as_view()),
    
    # Relationships # La pk es rara en esta tabla, la tiene en var y no en int, pero funciona bien
    path('relationship-types/', views.RelationshipTypeListCreate.as_view()),
    path('relationship-types/<str:pk>/', views.RelationshipTypeRetrieveUpdateDestroy.as_view()),
    path('relations/', views.RelationListCreate.as_view()),
    path('relations/<int:pk>/', views.RelationRetrieveUpdateDestroy.as_view()),
    
    # User-Deceased #Tiene problemas por ser pk compuesta (solo funciona el create) 
    path('user-deceased/', views.UserDeceasedListCreate.as_view()),
    path('user-deceased/<int:pk>/', views.UserDeceasedRetrieveUpdateDestroy.as_view()),
    
    # Requests #Tiene problemas por ser pk compuesta (solo funciona el create) 
    path('requests/', views.RequestListCreate.as_view()),
    path('requests/<int:pk>/', views.RequestRetrieveUpdateDestroy.as_view()),
    
    # Notifications
    path('notifications/', views.NotificationListCreate.as_view()),
    path('notifications/<int:pk>/', views.NotificationRetrieveUpdateDestroy.as_view()),
    
    # QR Codes
    path('qr-codes/', views.QRListCreate.as_view()),
    path('qr-codes/<int:pk>/', views.QRRetrieveUpdateDestroy.as_view()),

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
]