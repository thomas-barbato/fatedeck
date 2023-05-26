"""import """
import re
from pathlib import Path

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from core.models import Cards
from core.models import User


class CheckEmail:
    def validate(self, email):
        if User.objects.filter(email=email).exists() is True:
            raise ValidationError(
                _(
                    mark_safe(
                        '<div class="alert alert-warning text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                        "<p><b class='alert-black-text'>Votre adresse email doit être unique</b></p>"
                        "</div>"
                    )
                ),
                code="email_already_exists",
            )

    def get_help_text(self):
        """docstring"""
        return _(
            mark_safe(
                '<div class="alert alert-warning text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                "<p><b class='alert-black-text'>Votre adresse email doit être unique</b></p>"
                "</div>"
            )
        )


class CheckPasswordPolicy:
    """docstring"""

    def __init__(self):
        self.password_pattern = (
            "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        )

    def validate(self, password):
        """
        Has minimum 8 characters in length
        At least one uppercase letter. You can remove this condition by removing (?=.*?[A-Z])
        At least one lowercase letter. You can remove this condition by removing (?=.*?[a-z])
        At least one digit. You can remove this condition by removing (?=.*?[0-9])
        At least one special character, You can remove this condition by removing (?=.*?[#?!@$%^&*-])
        """
        if re.match(self.password_pattern, password) is None:
            raise ValidationError(
                _(
                    mark_safe(
                        '<div class="alert alert-warning text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                        "<p class='alert-black-text'><b>Votre mot de passe doit contenir à minima:</b></p>"
                        "<p class='alert-black-text'><b>8</b> caractères</p>"
                        "<p class='alert-black-text'><b>1</b> majuscule</p>"
                        "<p class='alert-black-text'><b>1</b> minuscule</p>"
                        "<p class='alert-black-text'><b>1</b> symbole</p>"
                        "<p class='alert-black-text'><b>1</b> chiffre</p>"
                        "</div>"
                    )
                ),
                code="password_too_weak",
            )

    def get_help_text(self):
        """docstring"""
        return _(
            '<div class="alert alert-dark" role="alert">'
            "<ul>"
            "<li class='alert-black-text'><b>Votre mot de passe doit contenir à minima:</b></li>"
            "<li class='alert-black-text'><b>8</b> caractères</li>"
            "<li class='alert-black-text'><b>1</b> majuscule</li>"
            "<li class='alert-black-text'><b>1</b> minuscule</li>"
            "<li class='alert-black-text'><b>1</b> symbole</li>"
            "<li class='alert-black-text'><b>1</b> chiffre</li>"
            "</ul>"
            "</div>"
        )


class CheckImageExtension:
    """docstring"""

    def __init__(self):
        self.table = Cards

    def validate(self, file):
        """
        check if extension is allowed.
        """
        allowed_extensions = [".jpg", ".png"]
        if not Path(file.name.lower()).suffixes[0] in allowed_extensions:
            raise ValidationError(
                _(
                    mark_safe(
                        '<div class="alert alert-warning text-center col-xl-12 col-md-12 col-sm-10 mt-1" role="alert">'
                        "<p><b><i class="
                        + '"fas fa-exclamation-triangle"'
                        + "></i> Extensions autorisées: .jpg et .png</b></p>"
                        "</div>"
                    )
                ),
                code="extension_not_allowed",
            )
