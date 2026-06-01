from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list_view, name='item_list'),
    path('create/', views.item_create_view, name='item_create'),
    path('<int:pk>/', views.item_detail_view, name='item_detail'),
    path('<int:pk>/delete/', views.item_delete_view, name='item_delete'),
    path('api/geocode/', views.nominatim_proxy, name='nominatim_proxy'),
    path('api/<int:pk>/claim/', views.ItemClaimAPIView.as_view(), name='item_claim_api'),
    path('api/<int:pk>/approve/', views.ItemApproveClaimAPIView.as_view(), name='item_approve_api'),
    path('api/<int:pk>/reject/', views.ItemRejectClaimAPIView.as_view(), name='item_reject_api'),
    path('dashboard/', views.user_dashboard_view, name='dashboard'),
    path('api/notifications/', views.UserNotificationsAPIView.as_view(), name='notifications_api'),
    path('api/notifications/<int:notification_id>/read/', views.MarkNotificationReadAPIView.as_view(), name='mark_notification_read_api'),
]
