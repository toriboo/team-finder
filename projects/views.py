from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Project
from .forms import ProjectForm


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if 'page' in query:
            del query['page']
        context['query_prefix'] = query.urlencode() + '&' if query else ''
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return redirect('projects:detail', pk=project.pk)


class EditProjectView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.owner

    def handle_no_permission(self):
        return redirect('projects:detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class CompleteProjectView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if request.user == project.owner and project.status == 'open':
            project.status = 'closed'
            project.save()
            return JsonResponse({'status': 'ok', 'project_status': 'closed'})
        return JsonResponse({'status': 'error'}, status=403)

    def test_func(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        return self.request.user == project.owner


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        # Закрытые проекты не принимают участников
        if project.status == 'closed':
            return JsonResponse({'status': 'error', 'message': 'Проект закрыт'}, status=403)

        # Владелец не может покинуть проект (он всегда в participants)
        if request.user == project.owner:
            return JsonResponse({'status': 'error', 'message': 'Владелец не может покинуть проект'}, status=403)

        # Переключаем участие
        if request.user in project.participants.all():
            project.participants.remove(request.user)
            joined = False
            participant = None
        else:
            project.participants.add(request.user)
            joined = True
            # Формируем объект участника так, как ожидает projects.js
            participant = {
                'id': request.user.id,
                'name': f"{request.user.name} {request.user.surname}",
                'avatar': request.user.avatar.url if request.user.avatar else None,
            }

        participants_count = project.participants.count()

        return JsonResponse({
            'status': 'ok',
            'joined': joined,
            'participants_count': participants_count,
            'participant': participant,
        })