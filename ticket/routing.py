from django.urls import path
from .consumers import ActivityConsumer

websocket_urlpatterns = [
    path('ws/activities/<int:project_id>/', ActivityConsumer.as_asgi()),
]