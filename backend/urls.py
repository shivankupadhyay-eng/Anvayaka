# core/urls.py
from django.urls import path, include
from rest_framework import routers
from . import views
from .views import LabourViewSet, StockViewSet, UserProfileViewSet, TaskViewSet, ParchiViewSet

router = routers.DefaultRouter()
router.register('labour', LabourViewSet)
router.register('stock', StockViewSet)
router.register('user-profile', UserProfileViewSet)
router.register('task', TaskViewSet)
router.register('parchi', ParchiViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mqtt/start/', views.start_mqtt_listener, name='start_mqtt'),
    path('mqtt/stop/', views.stop_mqtt_listener, name='stop_mqtt'),
    path('mqtt/status/', views.mqtt_listener_status, name='mqtt_status'),
]