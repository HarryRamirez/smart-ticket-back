from django.urls import path
from .views import TicketGenerateView, CreateTicketAPIView

urlpatterns = [
    path("generate/", TicketGenerateView.as_view(), name="ticket-generate"),
    path("create/", CreateTicketAPIView.as_view(), name="ticket-create"),
]