from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.template.response import TemplateResponse
from constance import config
from selectable.forms import AutoCompleteSelectMultipleWidget
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string

from projects.lookups import UserLookup
from .models import Project
from .forms import ProjectUpdateForm
from hackathons.models import Hackathon
from django.contrib.auth import get_user_model

User = get_user_model()


def get_helpful_display_name(self):
        return '{} ({})'.format(self.username, self.get_full_name())


User.add_to_class('__str__', get_helpful_display_name)


class CanRegisterMixin(object):
    def has_permissions(self):
        return config.ENABLE_REGISTRATION is True

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            return TemplateResponse(request, 'error.html', context={'error': 'Registration  is currently disabled.'}, status=400)
        else:
            return super(CanRegisterMixin, self).dispatch(request, *args, **kwargs)


class ProjectList(ListView):
    model = Project
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_hackathon = Hackathon.objects.get_current_hackathon()

        if current_hackathon:
            context['previous_hackathons'] = Hackathon.objects.exclude(id=current_hackathon.id)
            context['current_hackathon'] = current_hackathon

        return context


class ProjectCreate(LoginRequiredMixin, CanRegisterMixin, CreateView):
    login_url = '/login/'
    model = Project
    fields = ['title', 'looking_for_members', 'team', 'description']

    def form_valid(self, form):
        hackathon = self._get_current_hackathon()

        form.instance.hackathon = hackathon
        response = super(ProjectCreate, self).form_valid(form)

        form.instance.team.add(self.request.user)

        return response

    def _get_current_hackathon(self):
        try:
            r = Hackathon.objects.get_current_hackathon()
        except:
            print('Could find hackathon for this project')
            error_msg = 'Could not find a hackathon to associate with this \
                project. Please contact an administrator.'
            r = TemplateResponse(self.request, 'error.html', context={'error': error_msg},
                                 status=500)
        return r

    def get_form(self, *args, **kwargs):
        form = super(ProjectCreate, self).get_form(*args, **kwargs)
        form.fields['team'].widget = AutoCompleteSelectMultipleWidget(lookup_class=UserLookup,
                                                                      limit=10)
        form.fields['team'].widget.update_query_parameters({'hackathon':
                                                            self._get_current_hackathon()})
        return form


class ProjectDetail(DetailView):
    model = Project
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        liked = not project.can_like(self.request.user)
        can_edit = project.can_edit(self.request.user)
        can_delete = project.can_delete(self.request.user)
        can_request_to_join = project.can_request_to_join(self.request.user)
        context['liked'] = liked
        context['can_edit'] = can_edit
        context['can_delete'] = can_delete
        context['can_request_to_join'] = can_request_to_join
        return context


class ProjectUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    login_url = '/login/'
    model = Project
    form_class = ProjectUpdateForm
    template_name_suffix = '_update_form'
    raise_exception = True  # Permission denied instead of redirect to login page

    def test_func(self):
        project = self.get_object()
        return project.can_edit(self.request.user)


class ProjectDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    login_url = '/login/'
    model = Project
    success_url = reverse_lazy('project-list')
    raise_exception = True  # Permission denied instead of redirect to login page

    def test_func(self):
        project = self.get_object()
        return project.can_edit(self.request.user)


class ProjectLike(SingleObjectMixin, LoginRequiredMixin, View):
    model = Project

    def post(self, request, pk):
        project = self.get_object()

        if project.can_like(request.user):
            project.likes.add(request.user)
            return HttpResponse(status=201)

        return HttpResponse(status=400)

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return HttpResponse(401)

        project = self.get_object()
        liked = request.user.liked_projects.filter(pk=pk)

        if liked.exists():
            project.likes.remove(request.user)
            return HttpResponse(status=200)

        return HttpResponse(status=400)

class ProjectRequestToJoin(SingleObjectMixin, LoginRequiredMixin, View):
    model = Project

    def post(self, request, pk):
        project = self.get_object()

        if project.can_request_to_join(request.user):
            self.request_to_join_team(request)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)

    def request_to_join_team(self, request):
        project = self.get_object()
        with get_connection() as connection:
            msg_data = {
                'requester_name': request.user.get_full_name(),
                'requester_email': request.user.email,
                'project_name': project.title,
                'project_url': 'https://hackathon.adtran.com' + project.get_edit_url(),
                'hackathon_name': project.hackathon.formatted
            }
            title = 'Someone has requested to join your hackathon team'
            from_email = 'hackathon-noreply@adtran.com'
            msg_plain = render_to_string('emails/requested_to_join_team.txt', msg_data)
            msg_html = render_to_string('emails/requested_to_join_team.html', msg_data)
            recipient_list = [user.email for user in project.team.all()]
            send_mail(title, msg_plain, from_email, recipient_list, html_message=msg_html, connection=connection)
                