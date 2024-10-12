from django.contrib import admin
from django.urls import path, include

from base import views 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', views.UserProfileViews)
router.register('events', views.EventViewSet)

rsvp_add = views.RSVPViewSet.as_view({
    'get': 'list_rsvps',
    'post': 'rsvp_to_event',
})

rsvp_update = views.RSVPViewSet.as_view({
    'get': 'get_rsvp',
    'put': 'update_rsvp',
    'delete': 'delete_rsvp',
})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', include('base.urls')),
    path('api/events/<int:pk>/rsvp/', rsvp_add),
    path('api/events/<int:pk>/rsvp/<int:user_id>/', rsvp_update),
]