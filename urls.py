
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
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
    path(
        "new_game",
        core_views.CreateNewGameAjaxView.as_view(),
        name="create_game_view"
    ),
    path(
        "friendlist",
        core_views.DisplayAndAddFriendListView.as_view(),
        name="display-friend-list"
    ),
    path(
        "send-invitation-to-friend",
        core_views.DisplayAndAddFriendListView.as_view(),
        name="create-friend-invitation"
    ),
    path(
        "display-friend-invitation",
        core_views.FriendListInvitationView.as_view(),
        name="display-friend-invitation"
    ),
    path(
        "accept-or-deny-friend-invitation",
        core_views.FriendListInvitationView.as_view(),
        name="accept-or-deny-friend-invitation"
    ),
    path(
        "delete-friend",
        core_views.DeleteFriendView.as_view(),
        name="delete-friend"
    ),
    path(
        "ingame/<uuid:pk>",
        core_views.DisplayGame.as_view(template_name="display/ingame.html"),
        name="display_game_view"
    ),
    path(
        "ingame/players",
        core_views.DisplayFriendsAndPlayers.as_view(),
        name="display_friends_and_players_view"
    ),path(
        "ingame/sheet/<uuid:user_id>",
        core_views.DisplayPlayerCharacterSheet.as_view(template_name="display/character_sheet.html"),
        name="display_player_character_sheet"
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='user_logout',
    ),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
