from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DetailView, ListView, FormView
from .forms import RegisterForm, LoginForm, UserEditForm, ChangePasswordForm
from .models import User, Skill


# --- Регистрация и аутентификация ---
class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(FormView):
    form_class = LoginForm
    template_name = "users/login.html"
    success_url = reverse_lazy("projects:list")

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("projects:list")


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm
    template_name = "users/change_password.html"
    success_url = reverse_lazy("projects:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


# --- Профиль и редактирование ---
class UserDetailView(DetailView):
    model = User
    template_name = "users/user-details.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Дополнительные данные, если нужны
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "users/edit_profile.html"
    success_url = reverse_lazy("users:user_detail")

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy("users:user_detail", kwargs={"pk": self.request.user.pk})


# --- Список пользователей с фильтром по навыкам (Вариант 2) ---
class UserListView(ListView):
    model = User
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = 12
    ordering = ["id"]

    def get_queryset(self):
        qs = super().get_queryset()
        skill_name = self.request.GET.get("skill")
        if skill_name:
            qs = qs.filter(skills__name__iexact=skill_name)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_skills"] = Skill.objects.values_list("name", flat=True).order_by(
            "name"
        )
        context["active_skill"] = self.request.GET.get("skill", "")
        query = self.request.GET.copy()
        if "page" in query:
            del query["page"]
        context["query_prefix"] = query.urlencode() + "&" if query else ""
        return context


# --- API для работы с навыками (автодополнение, добавление, удаление) ---
class SkillAutocompleteView(View):
    def get(self, request):
        q = request.GET.get("q", "")
        if not q:
            return JsonResponse([], safe=False)
        skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:10]
        data = [{"id": s.id, "name": s.name} for s in skills]
        return JsonResponse(data, safe=False)


import json  # добавьте в начало файла


class AddUserSkillView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user_id = self.kwargs["user_id"]
        return self.request.user.id == user_id

    def post(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # Парсим JSON из тела запроса
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        skill_id = data.get("skill_id") or data.get("id")
        skill_name = data.get("name")
        created = False
        added = False

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
        elif skill_name:
            skill, created = Skill.objects.get_or_create(name=skill_name.strip())
        else:
            return JsonResponse({"error": "Не указан skill_id или name"}, status=400)

        if skill not in user.skills.all():
            user.skills.add(skill)
            added = True

        return JsonResponse(
            {"id": skill.id, "name": skill.name, "created": created, "added": added}
        )


class RemoveUserSkillView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user_id = self.kwargs["user_id"]
        return self.request.user.id == user_id

    def post(self, request, user_id, skill_id):
        user = get_object_or_404(User, id=user_id)
        skill = get_object_or_404(Skill, id=skill_id)
        user.skills.remove(skill)
        return JsonResponse({"status": "ok"})
