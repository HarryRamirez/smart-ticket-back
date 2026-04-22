from django.urls import path


from .views import ActivityAPIView, MemberSearchProjectAPIView, ProjectListAPIView, CreateProjectAPIView, GetProjectAPIView, ProjectMemberCreateAPIView, ProjectMemberDeleteAPIView, ProjectMemberUpdateRoleAPIView, ProjectMembersListAPIView, StatusProjectAPIView, UpdateProjectAPIView, DeleteProjectAPIView

urlpatterns = [
    path("list/", ProjectListAPIView.as_view(), name="project-list"),
    path("status_project/<int:pk>/", StatusProjectAPIView.as_view(), name="project-status"),
    path('<int:pk>/recent_activity/', ActivityAPIView.as_view()),
    path("create/", CreateProjectAPIView.as_view(), name="project-create"),
    path("<int:pk>/", GetProjectAPIView.as_view(), name="project-detail"),
    path("update/<int:pk>/", UpdateProjectAPIView.as_view(), name="project-update"),
    path("delete/", DeleteProjectAPIView.as_view(), name="project-delete"),
    path("<int:pk>/members/", ProjectMembersListAPIView.as_view(), name="project-members"),
    path("members/add/<int:pk>/", ProjectMemberCreateAPIView.as_view(), name="project-members-add"),
    path("<int:pk>/member/<int:member_id>/update/", ProjectMemberUpdateRoleAPIView.as_view(), name="project-members-update"),
    path("<int:pk>/member/<int:member_id>/delete/", ProjectMemberDeleteAPIView.as_view(), name="project-members-delete"),
    path('users/search/', MemberSearchProjectAPIView.as_view(), name='user-search'),
]