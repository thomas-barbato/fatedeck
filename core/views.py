import re
from datetime import datetime

import pytz
from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    TemplateView,
    FormView,
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    RedirectView,
    UpdateView,
)
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
    Gameinvitation,
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

    # TODO: This should not be necessary
    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def form_valid(self, form):
        # TODO: I think that this is depreacated in the last version of Django
        if self.request.is_ajax():
            # TODO: You could do this logic in the form, that's part of the validation
            #   Here it would just be if form.is_valid()
            if form.cleaned_data["password"] == form.cleaned_data["password2"]:
                form.save()
                response = {"status": 1}
                # TODO: Not sure this is necessary since you are using the mixin
                messages.success(self.request, self.get_success_message())
                return JsonResponse(response, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
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

    # TODO: This should not be necessary
    def get_success_message(self, cleaned_data=""):
        return self.success_message

    def get_success_url(self):
        return reverse_lazy("dashboard_view")

    def post(self, request, *args, **kwargs):
        # TODO: Could use a LoginRequiredMixin here?
        user = authenticate(
            self.request,
            username=self.request.POST.get("email").lower(),
            password=self.request.POST.get("password"),
        )
        response = ""

        if user is not None:
            # TODO: Why do you need to login and login back if user found?
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

        # TODO: This could go in a utils method to reduce the complexitiy in this view
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
        # TODO: This could go in a utils method to reduce the complexitiy in this view
        #   Why do you need to create a list of dictionary from values 🤔
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

        # TODO: Looks like a big copy/paste, DRY: Do not repeat yourself
        #   Can find an alternative to avoid code duplicate
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

        # TODO: Could you reverse this condition
        #   Like that you check this count and if >= 7 you raise an error
        #   I think this game_name, else sansnom could be in a clean in a form
        if Ingameplayer.objects.filter(player_id=self.request.user.id).count() < 7:
            if request.POST.get("game_name"):
                name = request.POST.get("game_name")
            else:
                name = "sansnom"

            # TODO: This block to generate a unique game code could in a util
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
        # TODO: Copy/Pasta?
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
            # TODO: All of this looks like something to validate the data, form?
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
        # TODO: Duplicates?
        friend_invitation = [
            {
                "name": elem["owner_uuid_id__username_invite_code"],
                "id": elem["id"],
            }
            for elem in Friendinviation.objects.select_related("owner_uuid_id") # TODO: Typo
            .filter(player_id=user_id)
            .values("id", "owner_uuid_id", "owner_uuid_id__username_invite_code")
        ]

        # TODO: I would rename the friend_invitation + _count to give it more sense
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
        contact = get_object_or_404(User, username_invite_code=self.request.POST.get("contact_name"))
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
        # TODO: Duplicates?
        players_list = [
            {
                "owner_uuid_id": player["owner_uuid_id"],
                "player_id": player["player_id"],
                "username_invite_code": player["player_id__username_invite_code"],
                "is_online": LoggedInUser.objects.filter(user_id=player["player_id"]).exists(),
            }
            for player in Ingameplayer.objects.filter(game_id=game.id).values(
                "owner_uuid_id",
                "player_id",
                "player_id__username_invite_code",
            )
        ]
        # TODO: Duplicates?
        friends_list = [
            {
                "player_id": friend["player_id"],
                "username_invite_code": friend["player_id__username_invite_code"],
            }
            for friend in Friendlist.objects.filter(owner_uuid_id=player_id)
            .exclude(
                player_id__in=[l["player_id"] for l in players_list],
            )
            .values(
                "owner_uuid_id",
                "player_id",
                "player_id__username_invite_code",
            )
        ]

        deck = (
            Ingamecards.objects.select_related("card")
            .filter(game_id=game.id)
            .values("card__filename", "card_id", "last_picked_up_by", "current_state")
            .order_by("?")
        )

        deck_count = Ingamecards.objects.filter(game_id=game.id, current_state="PIOCHE").count()

        context["game"] = game
        context["players"] = players_list
        context["friends"] = friends_list
        context["cards"] = deck
        context["deck_count"] = deck_count
        return context


class DisplayFriendsAndPlayers(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/ingame.html"

    def get(self, request, *args, **kwargs):
        game_id = self.request.GET.get("game_id")
        game = get_object_or_404(Game, id=game_id)
        player_id = self.request.user.id

        # TODO: Duplicates?
        players_list = [
            {
                "owner_uuid_id": player["owner_uuid_id"],
                "player_id": player["player_id"],
                "username_invite_code": player["player_id__username_invite_code"],
                "is_online": LoggedInUser.objects.filter(user_id=player["player_id"]).exists(),
            }
            for player in Ingameplayer.objects.filter(game_id=game.id).values(
                "owner_uuid_id",
                "player_id",
                "player_id__username_invite_code",
            )
        ]
        # TODO: Duplicates?
        friends_list = [
            {
                "player_id": friend["player_id"],
                "username_invite_code": friend["player_id__username_invite_code"],
            }
            for friend in Friendlist.objects.filter(owner_uuid_id=player_id)
            .exclude(
                player_id__in=[l["player_id"] for l in players_list],
            )
            .values(
                "player_id",
                "player_id__username_invite_code",
            )
        ]

        response_data = {"friends": friends_list, "players": players_list}

        return JsonResponse(response_data, safe=False)


class PlayerInvitationView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        # TODO: Remove duplicates when possible
        player_invitation = [
            {
                "contact_name": elem["owner_uuid_id__username_invite_code"],
                "game_name": elem["game_id__game_invite_code"],
                "id": elem["id"],
                "game_id": elem["game_id"],
            }
            for elem in Gameinvitation.objects.select_related("owner_uuid_id")
            .filter(player_id=user_id)
            .values(
                "id", "game_id", "owner_uuid_id", "owner_uuid_id__username_invite_code", "game_id__game_invite_code"
            )
        ]

        response_data = {
            "success": True,
            "game_invitation": len(player_invitation),
            "game_invitation_list": player_invitation,
        }
        return JsonResponse(response_data)

    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, id=request.POST.get("game_id"))
        invitation_by_select = request.POST.get("invitation_by_select")
        response_data = {}
        # TODO: Form :)
        if invitation_by_select in ["True", "False"]:
            if invitation_by_select == "True":
                player = get_object_or_404(User, id=request.POST.get("player_id"))
            else:
                player = get_object_or_404(User, username_invite_code=request.POST.get("player_id"))
            if game.id and player.id:
                # TODO: Form save?
                Gameinvitation.objects.create(
                    game_id=game.id, player_id=player.id, owner_uuid_id=request.POST.get("game_owner")
                )
            response_data = {"success": True}
        return JsonResponse(response_data, safe=False)


class AcceptOrDenyGameInvitation(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def post(self, request, *args, **kwargs):
        # TODO: This logic for me is doing validating so i could put that in a normal that
        if request.POST.get("choices") and request.POST.get("choices") in ["accept", "deny"]:
            choices = request.POST.get("choices")
            user_id = request.user.id
            contact_id = get_object_or_404(User, username_invite_code=request.POST.get("contact_name")).id
            game_id = get_object_or_404(Game, game_invite_code=request.POST.get("game_name")).id
            if choices == "accept":
                Ingameplayer.objects.create(player_id=user_id, owner_uuid_id=contact_id, game_id=game_id)
                Ingamecharactersheet.objects.create(owner_uuid_id=user_id, game_id=game_id)
            Gameinvitation.objects.get(owner_uuid_id=contact_id, player_id=user_id).delete()
            return JsonResponse({"success": True}, safe=False)


class DisplayPlayerCharacterSheet(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/character_sheet.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = get_object_or_404(Game, id=kwargs["pk"])
        player = get_object_or_404(Ingameplayer, game_id=game.id, player_id=kwargs["player_id"])
        # TODO: Could you just pass back the char in the context? or using values
        char = get_object_or_404(Ingamecharactersheet, game_id=game.id, owner_uuid_id=player.player_id)
        char_sheet = dict(
            {
                "charinfo": char.charinfo,
                "occupation": char.occupation,
                "aspect": char.aspect,
                "sub_aspect": char.sub_aspect,
                "attack": char.attack,
                "attack2": char.attack2,
                "skill": char.skill,
                "destiny": char.destiny,
                "spellbook": char.spellbook,
                "twist_deck": char.twist_deck,
                "origin": char.origin,
                "inventory": char.inventory,
                "talent": char.talent,
            }
        )

        context["character_sheet"] = char_sheet
        context["is_admin"] = bool(game.owner_uuid_id == self.request.user.id)
        return context

    # TODO: CreateView or UpdateView?
    def post(self, request):
        game_id = request.POST.get("game_id")
        owner_uuid_id = request.POST.get("player_id")
        char_info = json.loads(request.POST.get("character_information"))
        origin = json.loads(request.POST.get("origine"))
        occupation = json.loads(request.POST.get("occupation"))
        aspect = json.loads(request.POST.get("aspect"))
        sub_aspect = json.loads(request.POST.get("sub_aspect"))
        attack = json.loads(request.POST.get("attack"))
        attack2 = json.loads(request.POST.get("attack2"))
        skill = json.loads(request.POST.get("skill"))
        destiny = json.loads(request.POST.get("destiny"))
        talent = json.loads(request.POST.get("talent"))
        inventory = json.loads(request.POST.get("inventory"))
        spellbook = json.loads(request.POST.get("spellbook"))
        twist_deck = json.loads(request.POST.get("twist_deck"))

        tz_FR = pytz.timezone("Europe/Paris")
        datetime_FR = datetime.now(tz_FR)

        Ingamecharactersheet.objects.update_or_create(
            game_id=game_id,
            owner_uuid_id=owner_uuid_id,
            defaults={
                "game_id": game_id,
                "owner_uuid_id": owner_uuid_id,
                "charinfo": char_info,
                "origin": origin,
                "occupation": occupation,
                "aspect": aspect,
                "sub_aspect": sub_aspect,
                "attack": attack,
                "attack2": attack2,
                "skill": skill,
                "destiny": destiny,
                "talent": talent,
                "inventory": inventory,
                "spellbook": spellbook,
                "twist_deck": twist_deck,
                "created_at": datetime_FR,
                "updated_at": datetime_FR,
            },
        )
        response_data = {"success": True}
        return JsonResponse(response_data)


class PickACardView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/ingame.html"

    def post(self, request):
        game = get_object_or_404(Game, id=request.POST.get("game_id"))
        username = request.user.username_invite_code
        pick_order = Ingamecards.objects.filter(game_id=game.id, current_state="MAIN").count() + 1

        # TODO: Make it fail as soon as possible and the rest in the view will be the happy path
        if pick_order < 6:
            cards_drawn_id_list = Ingamecards.objects.filter(
                game_id=game.id, current_state="PIOCHE", order__isnull=True
            ).values_list("card_id", flat=True)

            update_card_id = (
                # TODO: Ingamecards.objects.filter(game_id=game.id) is used quite a lot
                #   How can you prevent duplicatas?
                Ingamecards.objects.filter(
                    card_id__in=cards_drawn_id_list,
                    game_id=game.id,
                    current_state="PIOCHE",
                    order__isnull=True,
                    last_picked_up_by__isnull=True,
                )
                .order_by("?")
                .values("id")
                .first()
            )

            tz_FR = pytz.timezone("Europe/Paris")
            datetime_FR = datetime.now(tz_FR)

            Ingamecards.objects.filter(id=update_card_id["id"]).update(
                current_state=str("MAIN"), order=pick_order, last_picked_up_by=username, updated_at=datetime_FR

            pick_card = [
                card
                for card in Ingamecards.objects.filter(
                    id=update_card_id["id"], game_id=game.id, current_state="MAIN", last_picked_up_by=username
                )
                .order_by("order")
                .values("card_id__filename", "card_id", "order", "last_picked_up_by", "id")
            ]

            response_data = {"success": True, "picked_card": pick_card, "deck_current_len": len(cards_drawn_id_list)}
        else:
            response_data = {
                "fail": True,
                "error_msg": "Vous ne pouvez pas tirer de cartes, votre zone de tirage est déjà pleine...",
            }
        return JsonResponse(response_data)


class GetCardsInformationsView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/ingame.html"

    def get(self, request, *args, **kwargs):
        game = get_object_or_404(Game, id=request.GET.get("game_id"))
        cards = [
            card
            for card in Ingamecards.objects.filter(game_id=game.id)
            .exclude(current_state="SPECIAL")
            .order_by("order")
            .values("id", "last_picked_up_by", "current_state", "card_id__filename")
        ]
        deck = [card["id"] for card in cards if card["current_state"] == "PIOCHE"]
        cemetery = [card["id"] for card in cards if card["current_state"] == "DEFAUSSE"]
        picked_card = [card for card in cards if card["current_state"] == "MAIN"]
        response_data = {"success": True, "cemetery": cemetery, "deck": deck, "picked_card": picked_card}
        return JsonResponse(response_data)


class CleanDrawnCardsView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/ingame.html"

    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, id=request.POST.get("game_id"))
        tz_FR = pytz.timezone("Europe/Paris")
        datetime_FR = datetime.now(tz_FR)
        Ingamecards.objects.filter(game_id=game.id, current_state="MAIN").update(
            current_state="DEFAUSSE", order=None, last_picked_up_by=None, updated_at=datetime_FR
        )
        response_data = {"success": True}
        return JsonResponse(response_data, safe=False)


class ResetDeckView(LoginRequiredMixin, JsonableResponseMixin, TemplateView):
    login_url = settings.LOGIN_URL
    template_name = "display/ingame.html"

    def post(self, request, *args, **kwargs):
        game = get_object_or_404(Game, id=request.POST.get("game_id"))
        # TODO: SHould this be in your settings?
        # TODO: Could create a utility method to isolate to do this, could be reusable somewhere else
        tz_FR = pytz.timezone("Europe/Paris")
        datetime_FR = datetime.now(tz_FR)
        # TODO: We usually use an enum to avoid to put choice value direcly
        # TODO: Can you reuse the first part of the request and prevent to do two request to DB here
        Ingamecards.objects.filter(game_id=game.id).exclude(current_state__in=["PIOCHE", "SPECIAL"]).update(
            current_state="PIOCHE", order=None, last_picked_up_by=None, updated_at=datetime_FR
        )
        # TODO: We usually use an enum to avoid to put choice value direcly
        deck = Ingamecards.objects.filter(game_id=game.id).exclude(current_state="SPECIAL").order("?").values("id")
        response_data = {"success": True, "deck": deck}
        return JsonResponse(response_data, safe=False)


class LeaveGameRedirectView(LoginRequiredMixin, JsonableResponseMixin, RedirectView):
    permanent = False
    query_string = True
    pattern_name = "dashboard_view"

    def get_redirect_url(self, *args, **kwargs):
        player = get_object_or_404(Ingameplayer, player_id=self.request.user.id)
        player.delete()
        return super().get_redirect_url(*args, **kwargs)
