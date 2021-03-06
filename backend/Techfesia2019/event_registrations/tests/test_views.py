from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from registration.models import User
from accounts.models import Institute, Profile
from events.models import TeamEvent, SoloEvent
from event_registrations.models import Team, TeamMember, TeamEventRegistration, SoloEventRegistration
import json
import datetime as dt


class TeamDetailEditDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser2@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name = 'staff',
                                              last_name = 'user',
                                              email = 'staff@test.com',
                                              is_staff = True
                                              )

        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.event = TeamEvent.objects.create(title='Sample Solo Event',
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=4,
                                              min_team_size=2
                                              )

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile1,
                                         name='Sample Team2'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1, invitation_accepted=True)

        self.registration = TeamEventRegistration.objects.create(team=self.team, event=self.event,
                                                                 is_reserved=self.team.is_reserved
                                                                 )

    def test_team_detail_view_unauthenticated(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.login(user=None)  # self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_detail_view_wrong_user(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_detail_view_team_does_not_exist(self):
        url = reverse('team_details', args=('random_string',))
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_team_detail_view(self):
        test_data = {
            'teamId': self.team.public_id,
            'name': 'Sample Team1',
            'leader': 'sample_test_user1',
            'members': ['sample_test_user2'],
            'invitees': [],
            'events': [],
        }
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['teamId'], test_data['teamId'])
        self.assertEqual(response.data['name'], test_data['name'])
        self.assertEqual(response.data['leader'], test_data['leader'])
        self.assertEqual(response.data['members'], test_data['members'])
        self.assertEqual(response.data['invitees'], test_data['invitees'])

    def test_team_detail_view_staff_user(self):
        test_data = {
            'teamId': self.team.public_id,
            'name': 'Sample Team1',
            'leader': 'sample_test_user1',
            'members': ['sample_test_user2'],
            'invitees': [],
            'events': [],
        }
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.staff_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['teamId'], test_data['teamId'])
        self.assertEqual(response.data['name'], test_data['name'])
        self.assertEqual(response.data['leader'], test_data['leader'])
        self.assertEqual(response.data['members'], test_data['members'])
        self.assertEqual(response.data['invitees'], test_data['invitees'])

    def test_team_edit_view_unauthenticated(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.login(user=None)  # self.client.logout()
        response = self.client.put(url,
                                   data=json.dumps({'name': 'New Team1'}),
                                   content_type='application/json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_edit_view_wrong_user(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.put(url,
                                   data=json.dumps({'name': 'New Team1'}),
                                   content_type='application/json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_edit_view_team_does_not_exist(self):
        url = reverse('team_details', args=('random_string',))
        self.client.force_login(user=self.user)
        response = self.client.put(url,
                                   data=json.dumps({'name': 'New Team1'}),
                                   content_type='application/json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_team_edit_view_no_name_input(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.put(url,
                                   data=json.dumps({}),
                                   content_type='application/json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_edit_view_name_not_unique(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.put(url,
                                   data=json.dumps({'name': 'Sample Team2'}),
                                   content_type='application/json'
                                   )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_edit_view(self):
        test_data = {
            'teamId': self.team.public_id,
            'name': 'New Team1',
            'leader': 'sample_test_user1',
            'members': ['sample_test_user2'],
            'invitees': [],
            'events': [],
        }
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.put(url,
                                   data=json.dumps({'name': 'New Team1'}),
                                   content_type='application/json'
                                   )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['teamId'], test_data['teamId'])
        self.assertEqual(response.data['name'], test_data['name'])
        self.assertEqual(response.data['leader'], test_data['leader'])
        self.assertEqual(response.data['members'], test_data['members'])
        self.assertEqual(response.data['invitees'], test_data['invitees'])

    def test_team_delete_view_unauthenticated(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.login(user=None)  # self.client.logout()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_delete_view_wrong_user(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_delete_view_team_does_not_exist(self):
        url = reverse('team_details', args=('random_string',))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_team_delete_view_registered_team(self):
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_delete_view(self):
        self.registration.delete()
        url = reverse('team_details', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamListCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.event = TeamEvent.objects.create(title='Sample Solo Event',
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=4,
                                              min_team_size=2
                                              )

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile1,
                                         name='Sample Team2'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1,
                                                      invitation_accepted=True)
        self.team1_member1 = TeamMember.objects.create(team=self.team1, profile=self.profile)

        self.registration = TeamEventRegistration.objects.create(team=self.team, event=self.event,
                                                                 is_reserved=self.team.is_reserved
                                                                 )

    def test_team_create_view_unauthenticated(self):
        url = reverse('teams_list_create')
        self.client.login(user=None)
        response = self.client.post(url, json.dumps({'name': 'Sample Team3'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_create_view_no_name_input(self):
        url = reverse('teams_list_create')
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_create_view_name_not_unique(self):
        url = reverse('teams_list_create')
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'name': 'Sample Team1'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_create_view(self):
        url = reverse('teams_list_create')
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'name': 'Sample Team3'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Team.objects.filter(team_leader=self.profile, name='Sample Team3').exists())

    def test_team_list_view_unauthenticated(self):
        url = reverse('teams_list_create')
        self.client.login(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_list_view_user(self):
        url = reverse('teams_list_create')
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_team_list_view_staff_user(self):
        url = reverse('teams_list_create')
        self.client.force_login(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamInvitationListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.event = TeamEvent.objects.create(title='Sample Solo Event',
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=4,
                                              min_team_size=2
                                              )

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile1,
                                         name='Sample Team2'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1,
                                                      invitation_accepted=True)
        self.team1_member1 = TeamMember.objects.create(team=self.team1, profile=self.profile)

        self.registration = TeamEventRegistration.objects.create(team=self.team, event=self.event,
                                                                 is_reserved=self.team.is_reserved
                                                                 )

    def test_team_invitation_list_view_unauthenticated(self):
        url = reverse('list_invitation', args=(self.user.username,))
        self.client.login(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_invitation_list_view_wrong_user(self):
        url = reverse('list_invitation', args=(self.user.username,))
        self.client.force_login(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_list_view(self):
        url = reverse('list_invitation', args=(self.user.username,))
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamInvitationDetailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1,
                                                      invitation_accepted=True)

    def test_team_invitation_detail_view_unauthenticated(self):
        url = reverse('invitation_detail', args=(self.user1.username, self.team.public_id))
        self.client.login(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_invitation_detail_view_wrong_user(self):
        url = reverse('invitation_detail', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_detail_view_wrong_username(self):
        url = reverse('invitation_detail', args=(self.user.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_detail_view_does_not_exist(self):
        url = reverse('invitation_detail', args=(self.user1.username, 'random_string'))
        self.client.force_login(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_detail_view(self):
        test_data = {
            'teamId': self.team.public_id,
            'name': self.team.name,
            'leader': self.user.username,
            'status': 'accepted'
        }
        url = reverse('invitation_detail', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_data['teamId'], response.data['teamId'])
        self.assertEqual(test_data['leader'], response.data['leader'])
        self.assertEqual(test_data['name'], response.data['name'])
        self.assertEqual(test_data['status'], response.data['status'])


class TeamInvitationAcceptViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1)

    def test_team_invitation_accept_view_unauthenticated(self):
        url = reverse('accept_invitation', args=(self.user1.username, self.team.public_id))
        self.client.login(user=None)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_invitation_accept_view_wrong_user(self):
        url = reverse('accept_invitation', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_accept_view_wrong_username(self):
        url = reverse('accept_invitation', args=(self.user.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_accept_view_does_not_exist(self):
        url = reverse('accept_invitation', args=(self.user1.username, 'random_string'))
        self.client.force_login(user=self.user1)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_accept_view_already_accepted(self):
        url = reverse('accept_invitation', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('accepted', response.data['status'])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_invitation_accept_view(self):
        self.assertEqual(self.team_member1.status, 'pending')
        test_data = {
            'teamId': self.team.public_id,
            'name': self.team.name,
            'leader': self.user.username,
            'status': 'accepted'
        }
        url = reverse('accept_invitation', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(test_data['teamId'], response.data['teamId'])
        self.assertEqual(test_data['leader'], response.data['leader'])
        self.assertEqual(test_data['name'], response.data['name'])
        self.assertEqual(test_data['status'], response.data['status'])


class TeamInvitationRejectViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1)

    def test_team_invitation_reject_view_unauthenticated(self):
        url = reverse('reject_invitation', args=(self.user1.username, self.team.public_id))
        self.client.login(user=None)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_invitation_reject_view_wrong_user(self):
        url = reverse('reject_invitation', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_reject_view_wrong_username(self):
        url = reverse('reject_invitation', args=(self.user.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_reject_view_does_not_exist(self):
        url = reverse('reject_invitation', args=(self.user1.username, 'random_string'))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_reject_view(self):
        self.assertEqual(self.team_member1.status, 'pending')
        url = reverse('reject_invitation', args=(self.user1.username, self.team.public_id))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TeamMember.objects.filter(team=self.team, profile=self.profile1).exists())


class TeamInvitationCreateViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )

        self.team2 = Team.objects.create(team_leader=self.profile,
                                         name='Sample Team2'
                                         )

        self.team_member = TeamMember.objects.create(team=self.team2, profile=self.profile1)

    def test_team_invitation_create_view_unauthenticated(self):
        url = reverse('create_invitation', args=(self.team.public_id,))
        self.client.login(user=None)
        response = self.client.post(url, json.dumps({'username': self.user1.username}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_invitation_create_view_wrong_user(self):
        url = reverse('create_invitation', args=(self.team.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.post(url, json.dumps({'username': self.user.username}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_create_view_team_does_not_exist(self):
        url = reverse('create_invitation', args=('random_string',))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'username': self.user1.username}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_create_view_user_does_not_exist(self):
        url = reverse('create_invitation', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'username': 'random_username'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_create_view_user_already_invited(self):
        url = reverse('create_invitation', args=(self.team2.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'username': self.user1.username}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_invitation_create_view_no_username_input(self):
        url = reverse('create_invitation', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_invitation_create_view_inviting_self(self):
        url = reverse('create_invitation', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'username': self.user.username}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_invitation_create_view(self):
        url = reverse('create_invitation', args=(self.team.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'username': self.user1.username}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TeamInvitationDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )

        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )
        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1)

    def test_team_invitation_delete_view_unauthenticated(self):
        url = reverse('delete_invitation', args=(self.team.public_id, self.user1.username,))
        self.client.login(user=None)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_invitation_delete_view_wrong_user(self):
        url = reverse('delete_invitation', args=(self.team.public_id, self.user1.username,))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_invitation_delete_view_team_does_not_exist(self):
        url = reverse('delete_invitation', args=('random_string', self.user1.username,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_delete_view_user_does_not_exist(self):
        url = reverse('delete_invitation', args=(self.team.public_id, 'random_string',))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_invitation_delete_view_invitation_accepted(self):
        self.team_member1.invitation_accepted = True
        self.team_member1.save()
        url = reverse('delete_invitation', args=(self.team.public_id, self.user1.username,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_invitation_delete_view(self):
        url = reverse('delete_invitation', args=(self.team.public_id, self.user1.username,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TeamMemberDeleteViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser2@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )

        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()

        self.event = TeamEvent.objects.create(title='Sample Team Event',
                                              team_event=True,
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=4,
                                              min_team_size=2
                                              )

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile,
                                         name='Sample Team2'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1, invitation_accepted=True)
        self.team1_member1 = TeamMember.objects.create(team=self.team1, profile=self.profile1, invitation_accepted=True)

        self.registration = TeamEventRegistration.objects.create(team=self.team1, event=self.event,
                                                                 is_reserved=self.team.is_reserved,
                                                                 is_complete=True,
                                                                 is_confirmed=True
                                                                 )

    def test_team_member_delete_view_unauthenticated(self):
        url = reverse('delete_member', args=(self.team.public_id, self.user1.username,))
        self.client.login(user=None)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_member_delete_view_wrong_user(self):
        url = reverse('delete_member', args=(self.team.public_id, self.user1.username,))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_member_delete_view_team_does_not_exist(self):
        url = reverse('delete_member', args=('random_string', self.user1.username,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_member_delete_view_not_a_member(self):
        url = reverse('delete_member', args=(self.team.public_id, 'random_string',))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_team_member_delete_view_team_registered(self):
        url = reverse('delete_member', args=(self.team1.public_id, self.user1.username,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_member_delete_view(self):
        url = reverse('delete_member', args=(self.team.public_id, self.user1.username,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventRegistrationDetailViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser2@test.com'
                                         )
        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user3',
                                         email='sampleuser3@test.com'
                                         )
        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )

        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()
        self.profile2 = Profile.objects.get(user=self.user2)
        self.profile2.college = self.institute
        self.profile2.save()

        self.event = TeamEvent.objects.create(title='Sample Solo Event',
                                              team_event=True,
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=4,
                                              min_team_size=2
                                              )

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile,
                                         name='Sample Team2'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile1, invitation_accepted=True)
        self.team1_member1 = TeamMember.objects.create(team=self.team1, profile=self.profile1, invitation_accepted=True)

        self.registration = TeamEventRegistration.objects.create(team=self.team1, event=self.event,
                                                                 is_reserved=self.team.is_reserved,
                                                                 is_complete=True,
                                                                 is_confirmed=True
                                                                 )

    def test_event_registration_detail_view_unauthenticated(self):
        url = reverse('event_registration_detail', args=(self.event.public_id,))
        self.client.login(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_registration_detail_view_registration_does_not_exist(self):
        url = reverse('event_registration_detail', args=(self.event.public_id,))
        self.client.force_login(user=self.user2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_event_registration_detail_view_member(self):
        url = reverse('event_registration_detail', args=(self.event.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_event_registration_detail_view(self):
        url = reverse('event_registration_detail', args=(self.event.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventRegistrationListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser2@test.com'
                                         )
        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user3',
                                         email='sampleuser3@test.com'
                                         )
        self.user3 = User.objects.create(username='sample_test_user4',
                                         first_name='sample',
                                         last_name='user4',
                                         email='sampleuser4@test.com'
                                         )

        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )

        self.institute = Institute.objects.create()

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()
        self.profile2 = Profile.objects.get(user=self.user2)
        self.profile2.save()
        self.profile3 = Profile.objects.get(user=self.user3)
        self.profile3.save()

        self.event = TeamEvent.objects.create(title='Sample Solo Event',
                                              team_event=True,
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=3,
                                              min_team_size=1
                                              )

        self.team = Team.objects.create(team_leader=self.profile3,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile,
                                         name='Sample Team2'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile2,
                                                      invitation_accepted=True)
        self.team1_member1 = TeamMember.objects.create(team=self.team1, profile=self.profile1,
                                                       invitation_accepted=True)

        self.registration = TeamEventRegistration.objects.create(team=self.team, event=self.event,
                                                                 is_reserved=self.team.is_reserved,
                                                                 is_complete=True,
                                                                 is_confirmed=True
                                                                 )

        self.registration1 = TeamEventRegistration.objects.create(team=self.team1, event=self.event,
                                                                  is_reserved=self.team.is_reserved,
                                                                  is_complete=True,
                                                                  is_confirmed=True
                                                                  )

    def test_event_registration_list_view_unauthenticated(self):
        url = reverse('list_event_registration', args=(self.event.public_id,))
        self.client.login(user=None)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_event_registration_list_view_event_does_not_exist(self):
        url = reverse('list_event_registration', args=('random_string',))
        self.client.force_login(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_event_registration_list_view_standard_user(self):
        url = reverse('list_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_event_registration_list_view_staff_user(self):
        url = reverse('list_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EventRegistrationViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='sample_test_user1',
                                        first_name='sample',
                                        last_name='user',
                                        email='sampleuser1@test.com'
                                        )
        self.user1 = User.objects.create(username='sample_test_user2',
                                         first_name='sample',
                                         last_name='user1',
                                         email='sampleuser2@test.com'
                                         )
        self.user2 = User.objects.create(username='sample_test_user3',
                                         first_name='sample',
                                         last_name='user2',
                                         email='sampleuser3@test.com'
                                         )
        self.user3 = User.objects.create(username='sample_test_user4',
                                         first_name='sample',
                                         last_name='user3',
                                         email='sampleuser4@test.com'
                                         )
        self.user4 = User.objects.create(username='sample_test_user5',
                                         first_name='sample',
                                         last_name='user4',
                                         email='sampleuser5@test.com'
                                         )

        self.staff_user = User.objects.create(username='staff',
                                              first_name='staff',
                                              last_name='user',
                                              email='staff@test.com',
                                              is_staff=True
                                              )

        self.institute = Institute.objects.create()
        self.institute1 = Institute.objects.create(name='Other Institute')

        self.profile = Profile.objects.get(user=self.user)
        self.profile.college = self.institute
        self.profile.save()
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.college = self.institute
        self.profile1.save()
        self.profile2 = Profile.objects.get(user=self.user2)
        self.profile2.college = self.institute1
        self.profile2.save()
        self.profile3 = Profile.objects.get(user=self.user3)
        self.profile3.college = self.institute1
        self.profile3.save()

        self.event = TeamEvent.objects.create(title='Sample Team Event',
                                              team_event=True,
                                              start_date=dt.date(2019, 7, 1),
                                              end_date=dt.date(2019, 7, 1),
                                              start_time=dt.time(12, 0, 0),
                                              end_time=dt.time(15, 0, 0),
                                              max_team_size=3,
                                              min_team_size=1
                                              )
        self.event1 = SoloEvent.objects.create(title='Sample Solo Event',
                                               start_date=dt.date(2019, 8, 3),
                                               end_date=dt.date(2019, 8, 4),
                                               start_time=dt.time(11, 0, 0),
                                               end_time=dt.time(15, 0, 0),
                                               )

        self.team = Team.objects.create(team_leader=self.profile,
                                        name='Sample Team1'
                                        )
        self.team1 = Team.objects.create(team_leader=self.profile3,
                                         name='Sample Team2'
                                         )
        self.team2 = Team.objects.create(team_leader=self.profile2,
                                         name='Sample Team3'
                                         )

        self.team_member1 = TeamMember.objects.create(team=self.team, profile=self.profile2,
                                                      invitation_accepted=True)
        self.team1_member1 = TeamMember.objects.create(team=self.team1, profile=self.profile1,
                                                       invitation_accepted=True)
        self.team2_member1 = TeamMember.objects.create(team=self.team2, profile=self.profile3)

        self.registration = TeamEventRegistration.objects.create(team=self.team, event=self.event,
                                                                 is_reserved=self.team.is_reserved,
                                                                 is_complete=True,
                                                                 is_confirmed=True
                                                                 )

        self.registration1 = SoloEventRegistration.objects.create(profile=self.profile, event=self.event1,
                                                                  is_reserved=self.profile.college == self.institute,
                                                                  is_complete=True,
                                                                  is_confirmed=True
                                                                  )
        self.registration2 = SoloEventRegistration.objects.create(profile=self.profile3, event=self.event1,
                                                                  is_reserved=self.profile3.college == self.institute,
                                                                  is_complete=True
                                                                  )

    def test_event_register_view_unauthenticated(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.login(user=None)
        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_solo_event_register_view_already_registered(self):
        url = reverse('create_event_registration', args=(self.event1.public_id,))
        self.client.force_login(user=self.user3)
        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_event_register_view_already_registered(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.post(url, json.dumps({'teamId': self.team.public_id}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.client.force_login(user=self.user2)
        response = self.client.post(url, json.dumps({'teamId': self.team1.public_id}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_event_register_view_not_team_leader(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user2)
        response = self.client.post(url, json.dumps({'teamId': self.team1.public_id}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_event_register_view_team_does_not_exist(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.post(url, json.dumps({'teamId': 'random_string'}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_solo_event_register_view(self):
        url = reverse('create_event_registration', args=(self.event1.public_id,))
        self.client.force_login(user=self.user2)
        response = self.client.post(url, json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SoloEventRegistration.objects.filter(event=self.event1, profile=self.profile2).exists())
        self.assertFalse(SoloEventRegistration.objects.get(event=self.event1, profile=self.profile2).is_reserved)

    def test_team_event_register_view_incomplete_team(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user3)
        response = self.client.post(url, json.dumps({'teamId': self.team2.public_id}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_event_register_view(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user3)
        response = self.client.post(url, json.dumps({'teamId': self.team1.public_id}), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamEventRegistration.objects.filter(event=self.event, team=self.team1).exists())
        self.assertFalse(TeamEventRegistration.objects.get(event=self.event, team=self.team1).is_reserved)

    def test_event_unregister_view_unauthenticated(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.login(user=None)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_solo_event_unregister_view_not_registered(self):
        url = reverse('create_event_registration', args=(self.event1.public_id,))
        self.client.force_login(user=self.user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_solo_event_unregister_view(self):
        url = reverse('create_event_registration', args=(self.event1.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_team_event_unregister_view_not_registered(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user1)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_team_event_unregister_view_not_leader(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user2)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_team_event_unregister_view(self):
        url = reverse('create_event_registration', args=(self.event.public_id,))
        self.client.force_login(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

