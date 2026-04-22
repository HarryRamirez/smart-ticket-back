from django.urls import path
from .views import TicketGenerateView, CreateTicketAPIView, TicketListAPIView, UpdateStatusTicketAPIView, UpcomingDueTicketsView

urlpatterns = [
    path("list/", TicketListAPIView.as_view(), name="ticket-list"),
    path("generate/", TicketGenerateView.as_view(), name="ticket-generate"),
    path("project/<int:project_id>/create/", CreateTicketAPIView.as_view(), name="ticket-create"),
    path("<int:pk>/update_status/", UpdateStatusTicketAPIView.as_view()),
    path('project/<int:project_id>/due_tickets/', UpcomingDueTicketsView.as_view()),
]