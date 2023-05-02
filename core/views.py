from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, FormView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Value, Q
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator

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
    Friendinviation,
)

from .forms import (
    LoginForm,
    RegisterForm
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
            login(self.request, user)
            response = {"status": 1}
            messages.success(self.request, self.get_success_message())
        return JsonResponse(response, safe=False)

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=200)


@method_decorator(AuthRequiredMiddleware, name="dispatch")
class DisplayDashboardView(TemplateView, LoginRequiredMixin):
    template_name = "display/dashboard.html"
    login_url = reverse_lazy('index_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        test = User.objects.select_related('ingameplayer').filter(id=self.request.user.id)
        print(test)
        context["max_game_per_user"] = 7

