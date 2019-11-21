from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.core import mail
from django.urls import reverse

from hackathons.models import Hackathon
from .models import Project


class AvailableParticipantsTestCase(TestCase):
    fixtures = ['hackathons.json', 'users.json',
                'profiles.json', 'bounties.json', 'projects.json']

    def setUp(self):
        pass

    def test_project_manager_should_return_no_participants_for_dead_hackathon(self):
        hackathon = Hackathon.objects.get(name='Hackathon XL 18.3')
        assert Project.objects.get_participants(hackathon) == []

    def test_project_manager_should_return_active_participants(self):
        expected = [User.objects.get(username='admin'), User.objects.get(username='UserA')]
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        actual = Project.objects.get_participants(hackathon)
        assert all(u in actual for u in expected)


class ProjectMemberNotificationsTestCase(TestCase):
    fixtures = ['hackathons.json', 'users.json',
                'bounties.json', 'profiles.json', 'projects.json']

    def setUp(self):
        self.admin = User.objects.get(username='admin')
        self.usera = User.objects.get(username='UserA')
        self.userb = User.objects.get(username='UserB')

    def check_email(self, email, action, hackathon, project, user):
        assert email.subject == f'You have been {action} "{project.title}"'
        assert email.from_email == 'hackathon-noreply@adtran.com'
        assert '<html>' in email.alternatives[0][0] # html
        assert action in email.body
        assert action in email.alternatives[0][0] # html
        assert project.title in email.body
        assert project.title in email.alternatives[0][0] # html
        assert hackathon.formatted in email.body
        assert hackathon.formatted in email.alternatives[0][0] # html
        project_url = 'https://hackathon.adtran.com' + project.get_absolute_url()
        assert project_url in email.body
        assert project_url in email.alternatives[0][0] # html
        assert user.first_name in email.body
        assert user.first_name in email.alternatives[0][0] # html
        assert email.to == [user.email]

    def test_notification_not_sent_after_creation_no_team(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.save()
        assert len(mail.outbox) == 0

    def test_notification_not_sent_after_editing_no_team(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.save()
        project.description = 'My description'
        project.save()
        assert len(mail.outbox) == 0

    def test_notification_not_sent_after_editing(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera)
        project.save()
        mail.outbox = []
        project.description = 'My description'
        project.save()
        assert len(mail.outbox) == 0

    def test_notification_after_creation_single_user(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera)
        project.save()

        assert len(mail.outbox) == 1
        self.check_email(mail.outbox[0], 'added to', hackathon, project, self.usera)

    def test_notifications_after_creation_multiple_users(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera, self.admin)
        project.save()

        assert len(mail.outbox) == 2
        self.check_email(mail.outbox[0], 'added to', hackathon, project, self.admin)
        self.check_email(mail.outbox[1], 'added to', hackathon, project, self.usera)

    def test_notifications_after_adding_single_user_to_project(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera)
        project.save()
        project.team.add(self.admin)
        project.save()

        assert len(mail.outbox) == 2
        self.check_email(mail.outbox[1], 'added to', hackathon, project, self.admin)

    def test_notifications_after_adding_multiple_users_to_project(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera)
        project.save()
        mail.outbox = []
        project.team.add(self.admin, self.userb)
        project.save()

        assert len(mail.outbox) == 2
        self.check_email(mail.outbox[0], 'added to', hackathon, project, self.admin)
        self.check_email(mail.outbox[1], 'added to', hackathon, project, self.userb)

    def test_notifications_after_removing_single_user_from_project(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera)
        project.save()
        mail.outbox = []
        project.team.remove(self.usera)
        project.save()

        assert len(mail.outbox) == 1
        self.check_email(mail.outbox[0], 'removed from', hackathon, project, self.usera)

    def test_notifications_after_removing_multiple_users_from_project(self):
        assert len(mail.outbox) == 0
        hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        project = Project(title='My new project', hackathon=hackathon, id=5)
        project.team.add(self.usera, self.userb)
        project.save()
        mail.outbox = []
        project.team.remove(self.usera, self.userb)
        project.save()

        assert len(mail.outbox) == 2
        self.check_email(mail.outbox[0], 'removed from', hackathon, project, self.usera)
        self.check_email(mail.outbox[1], 'removed from', hackathon, project, self.userb)


class ProjectRequestToJoinViewTestCase(TestCase):
    fixtures = ['hackathons.json', 'users.json', 'profiles.json']

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.get(username='admin')
        self.usera = User.objects.get(username='UserA')
        self.userb = User.objects.get(username='UserB')
        self.hackathon = Hackathon.objects.get(name='Hackathon 18.1')
        self.project = Project.objects.create(title='My new project', hackathon=self.hackathon)
        self.project.team.add(self.usera, self.userb)
        self.project.save()
        mail.outbox = []

    def check_email(self, email, requested_user, to):
        assert email.subject == 'Someone has requested to join your hackathon team'
        assert email.from_email == 'hackathon-noreply@adtran.com'
        assert '<html>' in email.alternatives[0][0] # html
        assert self.project.title in email.body
        assert self.project.title in email.alternatives[0][0] # html
        assert self.hackathon.formatted in email.body
        assert self.hackathon.formatted in email.alternatives[0][0] # html
        project_url = 'https://hackathon.adtran.com' + self.project.get_absolute_url() + 'edit/'
        assert project_url in email.body
        assert project_url in email.alternatives[0][0] # html
        assert requested_user.get_full_name() in email.body
        assert requested_user.get_full_name() in email.alternatives[0][0] # html
        assert email.to == to

    def test_user_not_logged_in(self):
        self.client.logout()
        response = self.client.post(reverse('project-request-to-join', kwargs={'pk': 1}), {})
        assert response.status_code == 302

    def test_user_not_on_requested_team(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('project-request-to-join', kwargs={'pk': 1}), {})
        assert response.status_code == 200
        assert len(mail.outbox) == 1
        self.check_email(mail.outbox[0], self.admin, [self.usera.email, self.userb.email])

    def test_user_already_on_team(self):
        self.client.force_login(self.userb)
        response = self.client.post(reverse('project-request-to-join', kwargs={'pk': 1}), {})
        assert response.status_code == 400
        assert len(mail.outbox) == 0

    def test_user_already_on_another_team(self):
        other_project = Project.objects.create(title='Other project', hackathon=self.hackathon)
        other_project.team.add(self.admin)
        other_project.save()
        mail.outbox = []

        self.client.force_login(self.admin)
        response = self.client.post(reverse('project-request-to-join', kwargs={'pk': 1}), {})
        assert response.status_code == 400
        assert len(mail.outbox) == 0