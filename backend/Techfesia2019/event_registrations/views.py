from accounts.models import Profile
from .models import Team, TeamMember
from .permissions import IsStaffUser, IsStaffUserOrPost, IsAuthenticatedOrPost
from .serializers import TeamSerializer, TeamMemberSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
# Create your views here.

# Team Views


class TeamDetailEditDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, public_id):
        try:
            return Team.objects.get(public_id=public_id)
        except Team.DoesNotExist:
            return Response({'message': 'Team Doesn\'t Exist.'}, status=status.HTTP_204_NO_CONTENT)

    def get(self, request, public_id, format=None):
        team = self.get_object(public_id)
        serializer = TeamSerializer(team)
        return Response(serializer.data)

    def delete(self, request, public_id, format=None):
        try:
            team = Team.objects.get(public_id=public_id)
            team.delete()
        except Team.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Team Deleted'}, status=status.HTTP_200_OK)

    def put(self, request, public_id, format=None):
        team = self.get_object(public_id=public_id)
        try:
            team.name = JSONParser().parse(request)['name']
            team.save()
        except KeyError:
            return Response({'message': 'required field "name" not provided'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TeamSerializer(team).data, status=status.HTTP_200_OK)


class TeamListCreateView(APIView):
    permission_classes = (IsAuthenticatedOrPost,)

    def get(self, request, format=None):
        teams = Team.objects.all()
        if not request.user.is_staff:
            profile = Profile.objects.get(user=request.user)
            teams = teams.filter(team_leader=profile)
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            user = request.user
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = JSONParser().parse(request)
        team = Team(name=data['name'], team_leader=profile)
        team.save()
        data = TeamSerializer(team).data
        return Response(data, status=status.HTTP_201_CREATED)


class TeamInvitationListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username, format=None):
        if not request.user.username == username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'message': 'User Profile is not complete'}, status=status.HTTP_400_BAD_REQUEST)
        invitations = TeamMember.objects.filter(profile=profile)
        serializer = TeamMemberSerializer(invitations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInvitationDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username, team_public_id, format=None):
        if not request.user.username == username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'message': 'User Profile is not complete'}, status=status.HTTP_400_BAD_REQUEST)
        invitation = TeamMember.objects.filter(profile=profile).get(team__public_id=team_public_id)
        serializer = TeamMemberSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInvitationAcceptView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, username, team_public_id, format=None):
        if not request.user.username == username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'message': 'User Profile is not complete'}, status=status.HTTP_400_BAD_REQUEST)
        invitation = TeamMember.objects.filter(profile=profile).get(team__public_id=team_public_id)
        if invitation.invitation_accepted:
            return Response({'error': 'Already Accepted'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            invitation.invitation_accepted = True
            invitation.save()
        serializer = TeamMemberSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamInvitationRejectView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, username, team_public_id, format=None):
        if not request.user.username == username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'message': 'User Profile is not complete'}, status=status.HTTP_400_BAD_REQUEST)
        invitation = TeamMember.objects.filter(profile=profile).get(team__public_id=team_public_id)
        if invitation.invitation_rejected:
            return Response({'error': 'Already Rejected'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            invitation.invitation_rejected = True
            invitation.invitation_accepted = False
            invitation.save()
        serializer = TeamMemberSerializer(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)
