import uuid
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.forms import JSONField
from django.db.models import JSONField
from django.utils.translation import ugettext_lazy as _

Logged_in_user = settings.AUTH_USER_MODEL

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", ".settings")



class MyUserManager(BaseUserManager):
    def create_user(self, email, password, first_name=None, last_name=None):
        if not email:
            raise ValueError("Vous devez entrer une adresse email.")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(user=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_staff = True
        user.save()
        return user

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=16, unique=False)
    email = models.EmailField(_('email address'), unique=True)
    username_invite_code = models.CharField(max_length=22, unique=True, null=True, blank=True)
    is_online = models.BooleanField(default=False)
    user_stylesheet = models.CharField(max_length=60, default="stylesheet_default_color.css", null=False)
    last_connection =  models.DateField('derniere connexion', auto_now_add=True, null=True, blank=True)
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField('update date', auto_now=True)
    deleted_at = models.DateTimeField('deletion date', null=True)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return f'{self.username}'

# Model to store the list of logged in users
class LoggedInUser(models.Model):
    user = models.OneToOneField(User, related_name='logged_in_user', on_delete=models.RESTRICT)
    # Session keys are 32 characters long
    session_key = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return self.user.email


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=16, unique=False, default="sans nom", null=False, blank=False)
    game_invite_code = models.CharField(max_length=22, unique=True, null=True, blank=True)
    owner_uuid = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField('update date', auto_now=True)
    deleted_at = models.DateTimeField('deletion date', null=True)


class Cards(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    filename = models.CharField(max_length=50)
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField('update date', auto_now=True)
    deleted_at = models.DateTimeField('deletion date', null=True)


class Ingameplayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                     related_name="ingameplayer_other_player_id")
    owner_uuid = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="ingameplayer_owner_id")
    last_connection = models.DateTimeField('derniere connexion', auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField('update date', auto_now=True)


class Ingamecards(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    card = models.ForeignKey(Cards, on_delete=models.CASCADE, null=True)
    current_state = models.CharField(max_length=8, unique=False, default="PIOCHE")
    # current_state can be : PIOCHE , MAIN , DEFAUSSE
    order = models.PositiveSmallIntegerField(null=True)
    last_picked_up_by = models.CharField(max_length=22, null=True, blank=True)
    updated_at = models.DateTimeField('update date', auto_now=True)


class Ingamecharactersheet(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    owner_uuid = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    charinfo = JSONField(default=dict)
    origin = JSONField(default=dict)
    occupation = JSONField(default=dict)
    aspect = JSONField(default=dict)
    sub_aspect = JSONField(default=dict)
    attack = JSONField(default=dict)
    attack2 = JSONField(default=dict)
    skill = JSONField(default=dict)
    destiny = JSONField(default=dict)
    talent = JSONField(default=dict)
    inventory = JSONField(default=dict)
    spellbook = JSONField(default=dict)
    twist_deck = JSONField(default=dict)
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField('update date', auto_now=True)


class Friendlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_uuid = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="friendlist_owner_id")
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                     related_name="friendlist_other_player_id")
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)


class Gameinviation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_uuid = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="game_owner_id")
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="game_other_player_id")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)


class Friendinviation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_uuid = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="invitation_owner_id")
    player = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                     related_name="invitation_other_player_id")
    created_at = models.DateTimeField('creation date', auto_now_add=True, null=True, blank=True)