from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.ProjectListView.as_view(), name="list"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("create-project/", views.CreateProjectView.as_view(), name="create"),
    path("<int:pk>/edit/", views.EditProjectView.as_view(), name="edit"),
    path("<int:pk>/complete/", views.CompleteProjectView.as_view(), name="complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.ToggleParticipateView.as_view(),
        name="toggle_participate",
    ),
]
