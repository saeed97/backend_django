from django.db import models
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import m2m_changed
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from hackathons.models import Hackathon
from bounties.models import Bounty


class ProjectManager(models.Manager):
    def get_participants(self, hackathon: Hackathon):
        projects = super().get_queryset().filter(hackathon=hackathon).all()
        teams = [p.team for p in projects]
        return [u for t in teams for u in t.all()]


class Project(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    looking_for_members = models.BooleanField('Looking for Members', default=True)
    description = models.TextField(blank=True)
    technologies = models.TextField(blank=True)
    inspiration = models.TextField(blank=True)
    what_it_does = models.TextField('What It Does', blank=True)
    how_it_was_built = models.TextField('How It Was Built', blank=True)
    challenges = models.TextField(blank=True)
    accomplishments = models.TextField(blank=True)
    learned = models.TextField(blank=True)
    whats_next = models.TextField('What\'s Next', blank=True)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL)
    hackathon = models.ForeignKey(Hackathon, on_delete=models.CASCADE)
    bounty = models.ForeignKey(Bounty, on_delete=models.CASCADE, blank=True, null=True)

    aws_resources = models.BooleanField('AWS Resources Requested', default=False)

    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_projects')

    objects = ProjectManager()

    def can_edit(self, user):
        if not user.is_authenticated:
            return False

        return self.team.filter(id=user.id).exists()

    def can_delete(self, user):
        return self.can_edit(user)

    def can_like(self, user):
        if not user.is_authenticated:
            return False

        return not self.likes.filter(id=user.id).exists()

    def can_request_to_join(self, user):
        return user.is_authenticated and user not in self.team.all() and not Project.objects.filter(team__id=user.id, hackathon=self.hackathon).exists()

    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return reverse('project-update', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title} ({self.hackathon})'

@receiver(m2m_changed, sender=Project.team.through)
def send_team_notifications(sender, instance, action, reverse, model, pk_set, **kwargs):
    # I don't feel like dealing with this right now since we aren't doing this anywhere in our code
    if reverse: return

    users = [User.objects.get(pk=pk) for pk in pk_set]

    if action == 'pre_add':
        title = f'You have been added to "{instance.title}"'
        template = 'emails/added_to_team'
    elif action == 'pre_remove':
        title = f'You have been removed from "{instance.title}"'
        template = 'emails/removed_from_team'
    else:
        return

    with get_connection() as connection:
        msg_data = {
            'title': title,
            'project_name': instance.title,
            'project_url': 'https://hackathon.adtran.com' + instance.get_absolute_url(),
            'hackathon_name': instance.hackathon.formatted
        }
        from_email = 'hackathon-noreply@adtran.com'
        for user in users:
            msg_data['name'] = user.first_name
            msg_plain = render_to_string(f'{template}.txt', msg_data)
            msg_html = render_to_string(f'{template}.html', msg_data)
            recipient_list = [user.email]
            send_mail(title, msg_plain, from_email, recipient_list, html_message=msg_html, connection=connection)