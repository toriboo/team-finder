from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import ProjectForm
from .models import Project, PROJECT_STATUS_OPEN, PROJECT_STATUS_CLOSED

PROJECTS_PER_PAGE = 12


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = PROJECTS_PER_PAGE
    ordering = ["-created_at"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if "page" in query:
            del query["page"]
        context["query_prefix"] = query.urlencode() + "&" if query else ""
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return redirect("projects:detail", pk=project.pk)


class EditProjectView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/create-project.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

    def handle_no_permission(self):
        return redirect("projects:detail", pk=self.kwargs["pk"])

    def get_success_url(self):
        # Используем reverse вместо reverse_lazy
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


class CompleteProjectView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        # Проверяем существование проекта без get_object_or_404
        project = Project.objects.filter(pk=pk).first()
        if not project:
            return JsonResponse(
                {"status": "error", "message": "Проект не найден"},
                status=HTTPStatus.NOT_FOUND,
            )

        if request.user == project.owner and project.status == PROJECT_STATUS_OPEN:
            project.status = PROJECT_STATUS_CLOSED
            project.save()
            return JsonResponse(
                {"status": "ok", "project_status": PROJECT_STATUS_CLOSED}
            )

        return JsonResponse({"status": "error"}, status=HTTPStatus.FORBIDDEN)

    def test_func(self):
        project = Project.objects.filter(pk=self.kwargs["pk"]).first()
        # Если проекта нет, доступа нет
        if not project:
            return False
        return self.request.user == project.owner

    def handle_no_permission(self):
        # Возвращаем JSON при отсутствии прав или проекта
        project_exists = Project.objects.filter(pk=self.kwargs["pk"]).exists()
        if not project_exists:
            return JsonResponse(
                {"status": "error", "message": "Проект не найден"},
                status=HTTPStatus.NOT_FOUND,
            )
        return JsonResponse(
            {"status": "error", "message": "Нет прав для завершения проекта"},
            status=HTTPStatus.FORBIDDEN,
        )


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = Project.objects.filter(pk=pk).first()
        if not project:
            return JsonResponse(
                {"status": "error", "message": "Проект не найден"},
                status=HTTPStatus.NOT_FOUND,
            )

        # Закрытые проекты не принимают участников
        if project.status == PROJECT_STATUS_CLOSED:
            return JsonResponse(
                {"status": "error", "message": "Проект закрыт"},
                status=HTTPStatus.FORBIDDEN,
            )

        # Владелец не может покинуть проект (он всегда в participants)
        if request.user == project.owner:
            return JsonResponse(
                {"status": "error", "message": "Владелец не может покинуть проект"},
                status=HTTPStatus.FORBIDDEN,
            )

        # Переключаем участие без загрузки всех записей
        is_participant = project.participants.filter(id=request.user.id).exists()
        if is_participant:
            project.participants.remove(request.user)
            joined = False
            participant = None
        else:
            project.participants.add(request.user)
            joined = True
            participant = {
                "id": request.user.id,
                "name": f"{request.user.name} {request.user.surname}",
                "avatar": request.user.avatar.url if request.user.avatar else None,
            }

        participants_count = project.participants.count()

        return JsonResponse(
            {
                "status": "ok",
                "joined": joined,
                "participants_count": participants_count,
                "participant": participant,
            }
        )
