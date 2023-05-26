from django.contrib.auth.hashers import make_password
from django.forms import forms, ModelForm, TextInput, PasswordInput
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import NON_FIELD_ERRORS

import re
from .models import (
    User,
    Game,
    Ingameplayer,
    Cards,
    Ingamecards,
    Friendlist,
    Ingamecharactersheet,
)
import datetime
from core.backend.check_data import CheckPasswordPolicy, CheckImageExtension, CheckEmail
import random


class RegisterForm(ModelForm):
    email = forms.EmailField(
        widget=TextInput(
            attrs={
                "class": "form-control text-center",
                "placeholder": "votre email...",
            }
        ),
        required=True,
        label="Email",
        help_text=CheckEmail().get_help_text(),
    )

    username = forms.CharField(
        widget=TextInput(
            attrs={
                "class": "form-control text-center",
                "placeholder": "Nom d'utilisateur",
            }
        ),
        required=True,
        label="Nom d'utilisateur",
    )

    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": "form-control mt-1 text-center",
                "placeholder": "Mot de passe",
            }
        ),
        required=True,
        label="Mot de passe",
        validators=[CheckPasswordPolicy().validate],
    )

    password2 = forms.CharField(
        widget=PasswordInput(
            attrs={
                "class": "form-control mt-1 text-center",
                "placeholder": "Confirmez le mot de passe",
            },
        ),
        required=True,
        label="Confirmation du mot de passe",
        validators=[CheckPasswordPolicy().validate],
        help_text=CheckPasswordPolicy().get_help_text(),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]
        exclude = ["user_id"]

    def save(self, password2, *args, **kwargs):
        s = super().save(password2)
        regexp_name = re.sub(
            r"([\$\!\#\_\&\"\£\*\%\?\^\ \=\[\]\{\}\(\)\:\=\<\>\;\§\%\~\|\_\^\@][\W]*)",
            "",
            self.instance.username.lower(),
        )
        if password2 == self.instance.password:
            username = re.sub(
                r"(^-+)|(^_+)|(^'+)|(^\.+)|(-$)|(_$)|('\.$)", "", regexp_name
            )
            self.instance.username = self.instance.username.lower()
            self.instance.email = self.instance.email
            self.instance.password = make_password(self.instance.password)
            self.instance.is_staff = False
            self.instance.is_active = True
            self.instance.date_joined = datetime.datetime.now()
            self.instance.username_invite_code = f"{username}#{random.randint(99,9999)}"
            super().save()


class LoginForm(ModelForm):
    """docstring"""

    email = forms.CharField(
        widget=TextInput(
            attrs={
                "label": "",
                "class": "form-control mb-1 form-input-text mb-3",
                "placeholder": "email...",
            }
        ),
        required=True,
    )
    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "label": "",
                "class": "form-control form-input-text mb-3",
                "placeholder": "Mot de passe...",
            }
        ),
        required=True,
    )

    class Meta:
        model = User
        fields = ["email", "password"]
        exclude = ["user_id"]


class CreateGameForm(ModelForm):
    name = forms.CharField(
        widget=TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "entrez le nom du jeu...",
                "minlength": 4,
                "maxlength": 16,
                "describedby": "input-game-name-help",
            }
        ),
        required=True,
    )

    class Meta:
        model = Game
        fields = ["name"]


class FriendInvitationForm(ModelForm):
    class Meta:
        model = Friendlist
        fields = []


class CharacterSheetForm(ModelForm):
    class Meta:
        model = Ingamecharactersheet
        fields = [
            "charinfo",
            "origin",
            "occupation",
            "aspect",
            "sub_aspect",
            "attack",
            "attack2",
            "skill",
            "destiny",
            "talent",
            "inventory",
            "spellbook",
            "twist_deck",
        ]

    def save(self, *args, **kwargs):
        self.instance.charinfo = kwargs["charinfo"]
        self.instance.origin = kwargs["origin"]
        self.instance.occupation = kwargs["occupation"]
        self.instance.aspect = kwargs["aspect"]
        self.instance.sub_aspect = kwargs["sub_aspect"]
        self.instance.attack = kwargs["attack"]
        self.instance.attack2 = kwargs["attack2"]
        self.instance.skill = kwargs["skill"]
        self.instance.destiny = kwargs["destiny"]
        self.instance.talent = kwargs["talent"]
        self.instance.inventory = kwargs["inventory"]
        self.instance.spellbook = kwargs["spellbook"]
        self.instance.twist_deck = kwargs["twist_deck"]
        super().save()
