import re
from datetime import datetime

import pytz
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView, CreateView, DetailView, DeleteView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Value, Q
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
import random
from django.shortcuts import get_object_or_404
from django.contrib.sessions.backends.base import SessionBase
import json
import settings
from core.backend.middlewares import JsonableResponseMixin, AuthRequiredMiddleware

from .models import (
    User,
    Game,
    Cards,
    Ingameplayer,
    Ingamecards,
    Ingamecharactersheet,
    Friendlist,
    Gameinviation,
    Friendinviation,
    LoggedInUser,
)

from .forms import LoginForm, RegisterForm, CreateGameForm, FriendInvitationForm


@method_decorator(csrf_exempt, name="dispatch")
class DisplayIndexView(FormView, SuccessMessageMixin):
    template_name = "index.html"
    form_class = LoginForm


@method_decorator(csrf_exempt, name="dispatch")
class CreateAccount(FormView, JsonableResponseMixin, SuccessMessageMixin):
    template_name = "create/user.html"
    form_class = RegisterForm
    success_message = (
        "<div class='alert alert-success text-center mt-1' role='alert'>"
        "<p class='alert-black-text'><b>Votre compte a été créé avec succès.</b></p>"
        "<p class='alert-black-text'>Vous pouvez des à présent vous connecter avec votre adresse email.</p>"
        "</div>"
    )

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def form_valid(self, form):
        if self.request.is_ajax():
            if form.cleaned_data["password"] == form.cleaned_data["password2"]:
                form.save()
                response = {"status": 1}
                messages.success(self.request, self.get_success_message())
                return JsonResponse(response, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        print(form)
        if self.request.is_ajax():
            response = {"status": 0, "errors": dict(form.errors.items())}
        return JsonResponse(response, status=200)


class LoginAjaxView(LoginView, JsonableResponseMixin, SuccessMessageMixin):
    class_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("dashboard_view")
    success_message = (
        "<div class='alert alert-success text-center mt-1' role='alert'>"
        "<p class='alert-black-text'><b>Vous êtes connecté</b></p>"
        "</div>"
    )

    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def get_success_url(self):
        return reverse_lazy("dashboard_view")

    def post(self, request, *args, **kwargs):
        user = authenticate(
            self.request,
            username=self.request.POST.get("email").lower(),
            password=self.request.POST.get("password"),
        )
        response = ""
        if user is not None:
            logout(request)
            login(self.request, user)
            response = {"status": 1}
            messages.success(self.request, self.get_success_message())
        return JsonResponse(response, safe=False)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=200)


class DisplayDashboardView(LoginRequiredMixin, ListView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        context["max_game_per_user"] = 7
        context["game_list_count"] = Ingameplayer.objects.filter(player_id=user_id).count()
        context["CreateGameForm"] = CreateGameForm
        context["game_list"] = [
            {
                "name": elem["game_id__name"],
                "id": elem["game_id"],
                "owner_uuid_id": elem["owner_uuid_id"],
            }
            for elem in Ingameplayer.objects.select_related("game_id")
            .filter(player_id=self.request.user.id)
            .values("game_id", "game_id__name", "owner_uuid_id")
        ]
        context["friends_list"] = [
            {
                "name": elem["player_id__username_invite_code"],
                "id": elem["id"],
                "is_online": LoggedInUser.objects.filter(user_id=elem["player_id"]).exists(),
            }
            for elem in Friendlist.objects.select_related("player_id")
            .filter(owner_uuid_id=user_id)
            .values("id", "player_id", "player_id__username_invite_code")
        ]
        return context


class CreateNewGameAjaxView(LoginRequiredMixin, JsonableResponseMixin, FormView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        cleaned_game_data = [
            {
                "name": elem["game_id__name"],
                "id": elem["game_id"],
                "owner_uuid_id": elem["owner_uuid_id"],
            }
            for elem in Ingameplayer.objects.select_related("game_id")
            .filter(player_id=user_id)
            .values("game_id", "game_id__name", "owner_uuid_id")
        ]
        response_data = {"success": True, "game_count": len(cleaned_game_data), "game_data": cleaned_game_data}
        return JsonResponse(response_data)

    def post(self, request, *args, **kwarg):
        if Ingameplayer.objects.filter(player_id=self.request.user.id).count() < 7:
            if request.POST.get("game_name"):
                name = request.POST.get("game_name")
            else:
                name = "sansnom"
            regexp_name = re.sub(r"[0-9][A-Z][a-z]", "", name)
            user_id = self.request.user.id
            game_invite_code = f"{regexp_name}#{random.randint(99, 9999)}"
            game = Game.objects.create(name=regexp_name, game_invite_code=game_invite_code, owner_uuid_id=user_id)

            Ingameplayer.objects.create(game_id=game.id, player_id=user_id, owner_uuid_id=user_id)

            for entry in Cards.objects.values("id", "name"):
                Ingamecards(
                    card_id=entry["id"],
                    current_state="PIOCHE" if entry["name"] != "dos" else "SPECIAL",
                    game_id=game.id,
                ).save()

            game_list_count = Ingameplayer.objects.filter(player_id=user_id).count()
            return JsonResponse(
                {
                    "success": True,
                    "game_list_count": game_list_count,
                    "game_data": {"name": game.name, "id": game.id, "owner_uuid_id": user_id},
                }
            )
        response_data = {"error": "Nombre de parties crées en simultané dépassé, 7 maximum."}
        return JsonResponse(response_data)


class DisplayAndAddFriendListView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        cleaned_friend_list = [
            {
                "name": elem["player_id__username_invite_code"],
                "id": elem["id"],
                "is_online": LoggedInUser.objects.filter(user_id=elem["player_id"]).exists(),
            }
            for elem in Friendlist.objects.select_related("player_id")
            .filter(owner_uuid_id=user_id)
            .values("id", "player_id", "player_id__username_invite_code")
        ]
        response_data = {"success": True, "friends": cleaned_friend_list}
        return JsonResponse(response_data)

    def post(self, request, *args, **kwargs):
        if self.request.POST.get("invite_code"):
            user = self.request.user
            friend_invitation_code = self.request.POST.get("invite_code")
            friend = get_object_or_404(User, username_invite_code=friend_invitation_code)
            if not friend.id:
                response_data = {"user_does_not_exists": True}
            elif user.username_invite_code == friend_invitation_code:
                response_data = {"error_same_user": True}
            elif Friendlist.objects.filter(
                Q(owner_uuid_id=user.id, player_id=friend.id) | Q(owner_uuid_id=friend.id, player_id=user.id)
            ).exists():
                response_data = {"already_friend_error": True}
            elif Friendinviation.objects.filter(
                Q(owner_uuid_id=user.id, player_id=friend.id) | Q(owner_uuid_id=friend.id, player_id=user.id)
            ).exists():
                response_data = {"invitation_already_sent": True}
            else:
                Friendinviation.objects.create(owner_uuid_id=user.id, player_id=friend.id)
                response_data = {"success": True}
        else:
            response_data = {"empty": True}
        return JsonResponse(response_data, safe=False)


class FriendListInvitationView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        friend_invitation = [
            {
                "name": elem["owner_uuid_id__username_invite_code"],
                "id": elem["id"],
            }
            for elem in Friendinviation.objects.select_related("owner_uuid_id")
            .filter(player_id=user_id)
            .values("id", "owner_uuid_id", "owner_uuid_id__username_invite_code")
        ]

        response_data = {
            "success": True,
            "friend_invitation": len(friend_invitation),
            "friend_invitation_list": friend_invitation,
        }
        return JsonResponse(response_data)

    def post(self, request, *args, **kwargs):
        if request.POST.get("choices") and request.POST.get("choices") in ["accept", "deny"]:
            choices = request.POST.get("choices")
            user_id = request.user.id
            contact_id = get_object_or_404(User, username_invite_code=request.POST.get("contact_name")).id
            if choices == "accept":
                Friendlist.objects.bulk_create(
                    [
                        Friendlist(
                            player_id=contact_id,
                            owner_uuid_id=user_id,
                        ),
                        Friendlist(
                            player_id=user_id,
                            owner_uuid_id=contact_id,
                        ),
                    ]
                )
            Friendinviation.objects.get(owner_uuid_id=contact_id, player_id=user_id).delete()
            return JsonResponse({"success": True}, safe=False)


class DeleteFriendView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL
    model = Friendlist

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        contact = get_object_or_404(User, username_invite_code=self.request.POST.get('contact_name'))
        response = {}
        if contact.id:
            friend = get_object_or_404(Friendlist, owner_uuid_id=user_id, player_id=contact.id).delete()
            friend = get_object_or_404(Friendlist, owner_uuid_id=contact.id, player_id=user_id).delete()
            response = {"success": True}
        return JsonResponse(response, safe=False)


class DisplayGame(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    model = Game
    template_name = "display/ingame.html"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game_id = self.kwargs["pk"]
        game = get_object_or_404(Game, id=game_id)
        player_id = self.request.user.id

        players_list = [
            {
                "owner_uuid_id": player["owner_uuid_id"],
                "player_id": player["player_id"],
                "username_invite_code": player["owner_uuid_id__username_invite_code"],
                "is_online": LoggedInUser.objects.filter(user_id=player["player_id"]).exists()
            }
            for player in Ingameplayer.objects.filter(game_id=game.id).values(
                "owner_uuid_id",
                "player_id",
                "owner_uuid_id__username_invite_code",
            )
        ]

        friends_list = [
            {
                "player_id": friend["player_id"],
                "username_invite_code": friend["owner_uuid_id__username_invite_code"],
            }
            for friend in Friendlist.objects.filter(
                owner_uuid_id=player_id
            ).exclude(
                player_id__in=[l['player_id'] for l in players_list],
                player_id__game__id=game.id,
            ).values(
                "owner_uuid_id",
                "player_id",
                "owner_uuid_id__username_invite_code",
            )
        ]

        deck = Ingamecards.objects.select_related('card').filter(game_id=game.id).values(
            'card__filename',
            'card_id',
            'last_picked_up_by',
            'current_state').order_by('?')

        deck_count = Ingamecards.objects.filter(game_id=game.id, current_state="PIOCHE").count()

        context['game'] = game
        context['players'] = players_list
        context['friends'] = friends_list
        context['cards'] = deck
        context['deck_count'] = deck_count
        return context


class DisplayFriendsAndPlayers(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/ingame.html"

    def get(self, request, *args, **kwargs):
        game_id = self.request.GET["game_id"]
        game = get_object_or_404(Game, id=game_id)
        player_id = self.request.user.id

        players_list = [
            {
                "owner_uuid_id": player["owner_uuid_id"],
                "player_id": player["player_id"],
                "username_invite_code": player["owner_uuid_id__username_invite_code"],
                "is_online": LoggedInUser.objects.filter(user_id=player["player_id"]).exists()
            }
            for player in Ingameplayer.objects.filter(game_id=game.id).values(
                "owner_uuid_id",
                "player_id",
                "owner_uuid_id__username_invite_code",
            )
        ]

        friends_list = [
            {
                "player_id": friend["player_id"],
                "username_invite_code": friend["owner_uuid_id__username_invite_code"],
            }
            for friend in Friendlist.objects.filter(
                owner_uuid_id=player_id
            ).exclude(
                player_id__in=[l['player_id'] for l in players_list],
            ).values(
                "player_id",
                "owner_uuid_id__username_invite_code",
            )
        ]

        response_data = {
            "friends" : friends_list,
            "players" : players_list
        }

        return JsonResponse(response_data, safe=False)


class DisplayPlayerCharacterSheet(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/character_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = get_object_or_404(Game, id=kwargs['pk'])
        player = get_object_or_404(Ingameplayer, game_id=game.id, player_id=kwargs['player_id'])
        character_sheet = [element for element in Ingamecharactersheet.objects.filter(game_id=game.id, owner_uuid_id=player.player_id).values(
            'charinfo',
            'occupation',
            'aspect',
            'sub_aspect',
            'attack',
            'attack2',
            'skill',
            'destiny',
            'spellbook',
            'twist_deck')]
        sheet_inventory_and_origins = [element for element in Ingamecharactersheet.objects.filter(game_id=game.id, owner_uuid_id=player.player_id).values(
            'origin', 'inventory')]
        sheet_inventory_talent = [element for element in Ingamecharactersheet.objects.filter(game_id=game.id, owner_uuid_id=player.player_id).order_by('id').values('talent')]

        sheet = list()
        for x in list(character_sheet):
            for key, value in x.items():
                for main_value in value:
                    sheet.append({key: {sub_key: sub_value for sub_key, sub_value in main_value.items()}, }, )

        context['character_sheet'] = sheet
        context['character_inventory_and_origins'] = sheet_inventory_and_origins
        context['sheet_inventory_talent'] = sheet_inventory_talent,
        return context

    def post(self, request):
        game_id = request.POST.get('game_id')
        owner_uuid_id = request.POST.get('player_id')
        char_info = json.loads(request.POST.get('character_information'))
        origin = json.loads(request.POST.get('origine'))
        occupation = json.loads(request.POST.get('occupation'))
        aspect = json.loads(request.POST.get('aspect'))
        sub_aspect = json.loads(request.POST.get('sub_aspect'))
        attack = json.loads(request.POST.get('attack'))
        attack2 = json.loads(request.POST.get('attack2'))
        skill = json.loads(request.POST.get('skill'))
        destiny = json.loads(request.POST.get('destiny'))
        talent = json.loads(request.POST.get('talent'))
        inventory = json.loads(request.POST.get('inventory'))
        spellbook = json.loads(request.POST.get('spellbook'))
        twist_deck = json.loads(request.POST.get('twist_deck'))

        tz_FR = pytz.timezone('Europe/Paris')
        datetime_FR = datetime.now(tz_FR)

        Ingamecharactersheet.objects.update_or_create(
            game_id=game_id,
            owner_uuid_id=owner_uuid_id,
            defaults={
                'game_id': game_id,
                'owner_uuid_id': owner_uuid_id,
                'charinfo': char_info,
                'origin': origin,
                'occupation': occupation,
                'aspect': aspect,
                'sub_aspect': sub_aspect,
                'attack': attack,
                'attack2': attack2,
                'skill': skill,
                'destiny': destiny,
                'talent': talent,
                'inventory': inventory,
                'spellbook': spellbook,
                'twist_deck': twist_deck,
                'created_at': datetime_FR,
                'updated_at': datetime_FR
            })
        response_data = {'success': True}
        return JsonResponse(response_data)

