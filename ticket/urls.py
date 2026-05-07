from django.urls import path


from .views import BacklogTicketsAPIView, TicketAssignToSprintAPIView, TicketAssignedToUpdateAPIView, TicketByStatusListAPIView, TicketDeleteAPIView, TicketGenerateView, CreateTicketAPIView, TicketListAPIView, UpdateStatusTicketAPIView, UpcomingDueTicketsView

urlpatterns = [
    path("project/<int:project_id>/list/", TicketListAPIView.as_view(), name="ticket-list"),
    path("generate/", TicketGenerateView.as_view(), name="ticket-generate"),
    path("project/<int:project_id>/create/", CreateTicketAPIView.as_view(), name="ticket-create"),
    path("<int:ticket_id>/project/<int:project_id>/update_status/", UpdateStatusTicketAPIView.as_view()),
    path('project/<int:project_id>/due_tickets/', UpcomingDueTicketsView.as_view()),
    path('project/<int:project_id>/backlog/', BacklogTicketsAPIView.as_view(), name='backlog-tickets'),
    path('<int:ticket_id>/project/<int:project_id>/assign/', TicketAssignToSprintAPIView.as_view(), name='assign-ticket-to-sprint'),
    path('project/<int:project_id>/tickets_by_status/', TicketByStatusListAPIView.as_view(), name='tickets-by-status'),
    path('<int:ticket_id>/project/<int:project_id>/assign-update/', TicketAssignedToUpdateAPIView.as_view(), name='ticket-assign'),
    path('<int:ticket_id>/project/<int:project_id>/delete/', TicketDeleteAPIView.as_view(), name='ticket-delete'),
]