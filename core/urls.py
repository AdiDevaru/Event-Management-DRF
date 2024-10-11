from django.contrib import admin
from django.urls import path, include

from base import views 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('userapi', views.UserProfileViews, basename='users')
router.register('eventapi', views.EventViewSet, basename='events')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]