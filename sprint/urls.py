from django.urls import path

from .views import SprintDeleteAPIView, SprintUpdateStatusAPIView, SprintUpdateAPIView, SprintCreateAPIView, SprintListAPIView

urlpatterns = [
    path('project/<int:project_id>/list/', SprintListAPIView.as_view(), name='sprint-list'),
    path('project/<int:project_id>/create/', SprintCreateAPIView.as_view(), name='sprint-create'),
    path('<int:sprint_id>/project/<int:project_id>/update-status/', SprintUpdateStatusAPIView.as_view(), name='sprint-update-status'),
    path('<int:sprint_id>/project/<int:project_id>/update/', SprintUpdateAPIView.as_view(), name='sprint-update'),
    path('<int:sprint_id>/project/<int:project_id>/delete/', SprintDeleteAPIView.as_view(), name='sprint-delete'),
]