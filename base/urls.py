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

review_add = views.ReviewViewSet.as_view({
    'get': 'get_review',
    'post': 'post_review',
})

review_update = views.ReviewViewSet.as_view({
    'get': 'get_review_details',
    'put': 'update_review',
    'delete': 'delete_review',
})

invitation_add = views.InvitationViewSet.as_view({
    'get': 'get_invitations',
    'post': 'post_invitations',
})

invitation_delete = views.InvitationViewSet.as_view({
    'get': 'get_invitation_details',
    'delete': 'delete_invitation',
})

urlpatterns = [
    path('', views.UserLoginView.as_view()),
    path('api/', include(router.urls)),
    path('api/events/<int:pk>/rsvp/', rsvp_add),
    path('api/events/<int:pk>/rsvp/<int:user_id>/', rsvp_update),
    path('api/events/<int:pk>/reviews/', review_add),
    path('api/events/<int:pk>/reviews/<int:review_id>/', review_update),
    path('api/events/<int:pk>/invitations/', invitation_add),
    path('api/events/<int:pk>/invitations/<int:invitation_id>', invitation_delete),
]
