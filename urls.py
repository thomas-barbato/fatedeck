
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from core import views as core_views

app_name = "core"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "",
        core_views.DisplayIndexView.as_view(template_name="index.html"),
        name="index_view",
    ),
    path(
        "register",
        core_views.CreateAccount.as_view(template_name="create/user.html"),
        name="register_view"
    ),
    path(
        "login",
        core_views.LoginAjaxView.as_view(),
        name="login_view",
    ),
    path(
        "dashboard",
        core_views.DisplayDashboardView.as_view(template_name="display/dashboard.html"),
        name="dashboard_view"
    ),
]
