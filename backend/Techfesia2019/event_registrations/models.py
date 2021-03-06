from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from accounts.models import Profile
from base.utils import generate_public_id
from django.utils.translation import gettext_lazy as _

from events.models import SoloEvent, TeamEvent


class Team(models.Model):
    public_id = models.CharField(max_length=100,
                                 unique=True,
                                 blank=True,
                                 db_index=True)

    name = models.CharField(max_length=20,
                            unique=True,
                            db_index=True
                            )

    team_leader = models.ForeignKey(to=Profile,
                                    on_delete=models.PROTECT
                                    )

    create_date = models.DateTimeField(auto_now_add=True)

    @property
    def team_members(self):
        name_list = []
        for i in self.teammember_set.all():
            name_list.append(i.profile.user.first_name + ' ' + i.profile.user.last_name)
        return ','.join(name_list)

    @property
    def leader(self):
        return self.team_leader.user

    @property
    def members(self):
        return self.teammember_set.filter(invitation_accepted=True)

    @property
    def invitees(self):
        return self.teammember_set.filter(invitation_accepted=False)

    @property
    def member_count(self):
        return 1 + self.teammember_set.filter(invitation_accepted=True).count()

    @property
    def is_reserved(self):
        try:
            if self.team_leader.college.name == 'Indian Institute of Information Technology, Sri City':
                for i in self.teammember_set.all():
                    try:
                        if i.profile.college.name != 'Indian Institute of Information Technology, Sri City':
                            return False
                    except:
                        return False
                return True
        except:
            return False
        return False

    def ready(self):
        return self.invitees.count() == 0

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = generate_public_id(self)

        super().save(*args, **kwargs)


class TeamMember(models.Model):
    team = models.ForeignKey(to=Team, on_delete=models.CASCADE, related_name='teammember_set')

    profile = models.ForeignKey(to=Profile, on_delete=models.PROTECT, related_name='member_teams')

    invitation_accepted = models.BooleanField(default=False,
                                              help_text="If true person has accepted invitation and is part of the team"
                                              )

    joined_on = models.DateTimeField(auto_now=True)

    @property
    def leader(self):
        return self.team.team_leader

    @property
    def team_name(self):
        return self.team.name

    @property
    def get_user_username(self):
        return self.profile.user.username

    @property
    def status(self):
        if self.invitation_accepted:
            return "accepted"
        else:
            return "pending"


class SoloEventRegistration(models.Model):
    public_id = models.CharField(max_length=100,
                                 unique=True,
                                 blank=True,
                                 db_index=True)

    event = models.ForeignKey(to=SoloEvent, on_delete=models.PROTECT)

    profile = models.ForeignKey(to=Profile, on_delete=models.CASCADE)

    is_complete = models.BooleanField(default=False,
                                      help_text="Tells whether user has completed all formalities like payments etc."
                                      )

    is_confirmed = models.BooleanField(default=False,
                                       help_text="Tells whether registration is confirmed or is in waiting"
                                       )

    is_reserved = models.BooleanField(default=False)

    created_on = models.DateTimeField(auto_now_add=True)

    updated_on = models.DateTimeField(auto_now=True)

    @property
    def status(self):
        if self.is_complete:
            if self.is_confirmed:
                return 'confirmed'
            else:
                return 'waiting'
        else:
            return 'payment pending'

    @property
    def fee(self):
        if self.is_reserved:
            return self.event.reserved_fee
        else:
            return self.event.fee

    def clean(self):
        if self.is_complete is False and self.is_confirmed is True:
            raise ValidationError(_("Registration can not be confirmed until it is complete"))

        if hasattr(self.profile, 'profileorganizer'):

            if self.profile.profileorganizer in self.event.organizers.all():
                raise ValidationError(_("Organizer can not be a participant for the same event"))

        if hasattr(self.profile, 'profilevolunteer'):

            if self.profile.profilevolunteer in self.event.volunteers.all():
                raise ValidationError(_("Volunteer can not be a participant for the same event"))

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = generate_public_id(self)

        super().save(*args, **kwargs)


class TeamEventRegistration(models.Model):
    public_id = models.CharField(max_length=100,
                                 unique=True,
                                 blank=True,
                                 db_index=True)

    event = models.ForeignKey(to=TeamEvent, on_delete=models.PROTECT)

    team = models.ForeignKey(to=Team, on_delete=models.CASCADE, related_name='events')

    is_complete = models.BooleanField(default=False,
                                      help_text="Tells whether a team has completed all formalities like payments etc."
                                      )

    is_confirmed = models.BooleanField(default=False,
                                       help_text="Tells whether registration is confirmed or is in waiting"
                                       )

    created_on = models.DateTimeField(auto_now_add=True)

    updated_on = models.DateTimeField(auto_now=True)

    is_reserved = models.BooleanField(default=False)

    @property
    def event_type(self):
        return 'team'

    @property
    def fee(self):
        if self.is_reserved:
            return self.event.reserved_fee
        else:
            return self.event.fee

    @property
    def get_event_public_id(self):
        return self.event.public_id

    @property
    def status(self):
        if self.is_complete:
            if self.is_confirmed:
                return 'confirmed'
            else:
                return 'waiting'
        else:
            return 'payment pending'

    def clean(self):
        if self.is_complete is False and self.is_confirmed is True:
            raise ValidationError(_("Registration can not be confirmed until it is complete"))

    # TODO: A check required that ensures no team member is an organizer/volunteer for same event
    # Doing it here however might be too expensive

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = generate_public_id(self)

        super().save(*args, **kwargs)
