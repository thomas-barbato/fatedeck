# Generated by Django 3.2.18 on 2023-04-28 20:10

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('username_invite_code', models.CharField(blank=True, max_length=22, null=True, unique=True)),
                ('is_online', models.BooleanField(default=False)),
                ('user_stylesheet', models.CharField(default='stylesheet_default_color.css', max_length=60)),
                ('last_connection', models.DateTimeField(auto_now_add=True, null=True, verbose_name='derniere connexion')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deletion date')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cards',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('filename', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deletion date')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default='sans nom', max_length=16)),
                ('game_invite_code', models.CharField(blank=True, max_length=22, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('deleted_at', models.DateTimeField(null=True, verbose_name='deletion date')),
                ('owner_uuid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Pargen',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default='pargen_default_option', max_length=60)),
                ('int_value', models.IntegerField(blank=True, null=True)),
                ('str_value', models.CharField(blank=True, max_length=60, null=True)),
                ('bool_value', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ingameplayer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('last_connection', models.DateTimeField(auto_now_add=True, null=True, verbose_name='derniere connexion')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('id_game_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('id_player_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingameplayer_other_player_id', to=settings.AUTH_USER_MODEL)),
                ('owner_uuid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ingameplayer_owner_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ingamecharactersheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('charinfo', models.JSONField(default=dict)),
                ('origin', models.JSONField(default=dict)),
                ('occupation', models.JSONField(default=dict)),
                ('aspect', models.JSONField(default=dict)),
                ('sub_aspect', models.JSONField(default=dict)),
                ('attack', models.JSONField(default=dict)),
                ('attack2', models.JSONField(default=dict)),
                ('skill', models.JSONField(default=dict)),
                ('destiny', models.JSONField(default=dict)),
                ('talent', models.JSONField(default=dict)),
                ('inventory', models.JSONField(default=dict)),
                ('spellbook', models.JSONField(default=dict)),
                ('twist_deck', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('id_game_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('owner_uuid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ingamecards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_state', models.CharField(default='PIOCHE', max_length=8)),
                ('order', models.PositiveSmallIntegerField(null=True)),
                ('last_picked_up_by', models.CharField(blank=True, max_length=22, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='update date')),
                ('id_card_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.cards')),
                ('id_game_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.game')),
            ],
        ),
        migrations.CreateModel(
            name='Gameinviation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('id_game_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.game')),
                ('id_player_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_other_player_id', to=settings.AUTH_USER_MODEL)),
                ('owner_uuid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='game_owner_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friendlist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('id_player_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friendlist_other_player_id', to=settings.AUTH_USER_MODEL)),
                ('owner_uuid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='friendlist_owner_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Friendinviation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='creation date')),
                ('id_player_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitation_other_player_id', to=settings.AUTH_USER_MODEL)),
                ('owner_uuid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='invitation_owner_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]