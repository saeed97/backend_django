from django.contrib.auth.models import User
from selectable.base import ModelLookup
from selectable.registry import registry

from hackathons.models import Hackathon
from .models import Project


class UserLookup(ModelLookup):
    model = User
    search_fields = (
        'username__icontains',
        'first_name__icontains',
        'last_name__icontains',
    )
    filters = {'is_active': True, }

    def get_query(self, request, term):
        auto_users = super().get_query(request, term)

        participants = self._get_all_participants(request)
        return list(filter(lambda u: u not in participants, auto_users))

    def _get_all_participants(self, request):
        form_hackathon = request.GET.get('hackathon', '')
        hackathon = Hackathon.objects.get(name=form_hackathon)
        return Project.objects.get_participants(hackathon)


registry.register(UserLookup)
