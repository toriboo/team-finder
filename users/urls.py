from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Страницы аутентификации и профиля
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path(
        "change-password/", views.ChangePasswordView.as_view(), name="change_password"
    ),
    path("edit-profile/", views.EditProfileView.as_view(), name="edit_profile"),
    path("list/", views.UserListView.as_view(), name="user_list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    # API для навыков (автодополнение, добавление, удаление)
    path("skills/", views.SkillAutocompleteView.as_view(), name="skill_autocomplete"),
    path(
        "<int:user_id>/skills/add/",
        views.AddUserSkillView.as_view(),
        name="add_user_skill",
    ),
    path(
        "<int:user_id>/skills/<int:skill_id>/remove/",
        views.RemoveUserSkillView.as_view(),
        name="remove_user_skill",
    ),
]
