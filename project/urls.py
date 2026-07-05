from django.urls import path


from .views import ActivityAPIView, DashboardCardsAPIView, DashboardTicketsRecenAPIView, MemberSearchProjectAPIView, ProjectActiveAPIView, ProjectDeleteAPIView, ProjectListAPIView, CreateProjectAPIView, RetrieveProjectAPIView, ProjectMemberCreateAPIView, ProjectMemberDeleteAPIView, ProjectMemberUpdateRoleAPIView, ProjectMembersListAPIView, StatusCreateAPIView, StatusDeleteAPIView, StatusProjectAPIView, StatusUpdateAPIView, UpdateProjectAPIView, DeleteProjectAPIView

urlpatterns = [
    path("list/", ProjectListAPIView.as_view(), name="project-list"),
    path("status_project/<int:pk>/", StatusProjectAPIView.as_view(), name="project-status"),
    path('<int:pk>/recent_activity/', ActivityAPIView.as_view()),
    path("create/", CreateProjectAPIView.as_view(), name="project-create"),
    path("<int:pk>/", RetrieveProjectAPIView.as_view(), name="project-detail"),
    path("<int:project_id>/update/", UpdateProjectAPIView.as_view(), name="project-update"),
    path("delete/", DeleteProjectAPIView.as_view(), name="project-delete"),
    path("<int:pk>/members/", ProjectMembersListAPIView.as_view(), name="project-members"),
    path("members/add/<int:pk>/", ProjectMemberCreateAPIView.as_view(), name="project-members-add"),
    path("<int:pk>/member/<int:member_id>/update/", ProjectMemberUpdateRoleAPIView.as_view(), name="project-members-update"),
    path("<int:pk>/member/<int:member_id>/delete/", ProjectMemberDeleteAPIView.as_view(), name="project-members-delete"),
    path('users/search/', MemberSearchProjectAPIView.as_view(), name='user-search'),
    path("dashboard/cards/", DashboardCardsAPIView.as_view(), name="dashboard-cards"),
    path('<int:project_id>/status/', StatusCreateAPIView.as_view(), name='create-status'),
    path('<int:project_id>/status/<int:status_id>/update/', StatusUpdateAPIView.as_view(), name='update-status'),
    path('<int:project_id>/delete/', ProjectDeleteAPIView.as_view(), name='delete-project'),
    path('<int:project_id>/status/<int:status_id>/delete/', StatusDeleteAPIView.as_view(), name='delete-status'),
    path('active/', ProjectActiveAPIView.as_view(), name='active-projects'),
    path('dashboard_recent_tickets/', DashboardTicketsRecenAPIView.as_view(), name='dashboard-recent-tickets'),
]