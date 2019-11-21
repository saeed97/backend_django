from django.forms import ModelForm
from selectable.forms import AutoCompleteSelectMultipleField, \
    AutoCompleteSelectMultipleWidget, AutoCompleteSelectField, AutoCompleteSelectWidget

from bounties.lookups import BountyLookup
from projects.lookups import UserLookup
from .models import Project
from constance import config


class ProjectUpdateForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'looking_for_members', 'aws_resources', 'description', 'bounty',
                  'technologies', 'team',
                  'image', 'inspiration',
                  'what_it_does', 'how_it_was_built', 'challenges',
                  'accomplishments', 'learned', 'whats_next']

        team = AutoCompleteSelectMultipleField(lookup_class=UserLookup,
                                               widget=AutoCompleteSelectMultipleWidget(
                                                   lookup_class=UserLookup, limit=10),
                                               label="Select a team member")
        bounty = AutoCompleteSelectField(lookup_class=BountyLookup,
                                         widget=AutoCompleteSelectWidget(
                                             lookup_class=BountyLookup, limit=10),
                                         label="Select a team member")
        widgets = {
            'team': AutoCompleteSelectMultipleWidget(lookup_class=UserLookup, limit=10),
            'bounty': AutoCompleteSelectWidget(lookup_class=BountyLookup, limit=10)
        }

    def __init__(self, *args, **kwargs):
        super(ProjectUpdateForm, self).__init__(*args, **kwargs)
        self.fields['team'].widget.update_query_parameters({'hackathon':
                                                             self.instance.hackathon})
        if not config.AWS_RESOURCES_AVAILABLE:
            del self.fields['aws_resources']
