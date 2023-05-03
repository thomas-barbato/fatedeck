import re
from datetime import datetime

from django.shortcuts import render, redirect
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView, ListView, CreateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Value, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
import random
from django.contrib.sessions.backends.base import SessionBase

import settings
from core.backend.middlewares import (
    JsonableResponseMixin,
    AuthRequiredMiddleware
)

from .models import (
    User,
    Game,
    Cards,
    Ingameplayer,
    Ingamecards,
    Ingamecharactersheet,
    Friendlist,
    Gameinviation,
    Friendinviation, LoggedInUser,
)

from .forms import (
    LoginForm,
    RegisterForm, CreateGameForm
)


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
        context["game_list"] = [{'name':elem['game_id__name'], 'id':elem['game_id'], 'owner_uuid_id':elem['owner_uuid_id'],} for elem in Ingameplayer.objects.select_related('game_id').filter(player_id=self.request.user.id).values('game_id', 'game_id__name', 'owner_uuid_id')]

        return context

class CreateNewGameAjaxView(LoginRequiredMixin, JsonableResponseMixin, FormView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        cleaned_game_data = [
            {'name':elem['game_id__name'], 'id':elem['game_id'], 'owner_uuid_id':elem['owner_uuid_id'],} for elem in Ingameplayer.objects.select_related('game_id').filter(player_id=user_id).values('game_id', 'game_id__name', 'owner_uuid_id')
        ]
        response_data = {
            'success': True,
            'game_count' : len(cleaned_game_data),
            'game_data': cleaned_game_data
        }
        return JsonResponse(response_data)

    def post(self, request, *args, **kwarg):
        if Ingameplayer.objects.filter(player_id=self.request.user.id).count() < 7:
            if request.POST.get('game_name'):
                name = request.POST.get('game_name')
            else:
                name = "sansnom"
            regexp_name = re.sub(r"[0-9][A-Z][a-z]", '',name)
            user_id = self.request.user.id
            game_invite_code = f'{regexp_name}#{random.randint(99, 9999)}'
            game = Game(
                name=regexp_name,
                game_invite_code=game_invite_code,
                owner_uuid_id=user_id
            )
            game.save()
            game_id = Game.objects.filter(
                name=name,
                game_invite_code=game_invite_code,
                owner_uuid_id=user_id
            ).values('id')

            player = Ingameplayer(
                game_id=game_id,
                player_id=user_id,
                owner_uuid_id=user_id
            )
            player.save()

            for entry in Cards.objects.values('id', 'name'):
                Ingamecards(
                    card_id=entry['id'],
                    current_state="PIOCHE" if entry['name'] != 'dos' else 'SPECIAL',
                    game_id=game_id
                ).save()

            game_list_count = Ingameplayer.objects.filter(player_id=user_id).count()
            return JsonResponse({
                'success': True,
                'game_list_count': game_list_count,
                'game_data': {'name': game.name, 'id': game.id,
                              'owner_uuid_id': user_id }
            })
        response_data = {'error': 'Nombre de parties crées en simultané dépassé, 7 maximum.'}
        return JsonResponse(response_data)


class DisplayFriendListView(LoginRequiredMixin, JsonableResponseMixin, FormView):
    template_name = "display/dashboard.html"
    login_url = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        user_id = self.request.user.id
        cleaned_friend_list = [
            {'name':elem['player_id__username_invite_code'],
             'id':elem['id'],
             'is_online': LoggedInUser.objects.filter(user_id=elem['player_id']).exists(),
             } for elem in Friendlist.objects.select_related('player_id').filter(owner_uuid_id=user_id).values('id','player_id', 'player_id__username_invite_code', 'player_id__last_connection')
        ]
        print(cleaned_friend_list)
        response_data = {
            'success': True,
            'friends': cleaned_friend_list
        }
        return JsonResponse(response_data)

