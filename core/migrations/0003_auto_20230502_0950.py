# Generated by Django 3.2.18 on 2023-05-02 07:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_alter_user_username"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Pargen",
        ),
        migrations.RenameField(
            model_name="friendinviation",
            old_name="id_player_id",
            new_name="player",
        ),
        migrations.RenameField(
            model_name="friendlist",
            old_name="id_player_id",
            new_name="player",
        ),
        migrations.RenameField(
            model_name="gameinviation",
            old_name="id_game_id",
            new_name="game",
        ),
        migrations.RenameField(
            model_name="gameinviation",
            old_name="id_player_id",
            new_name="player",
        ),
        migrations.RenameField(
            model_name="ingamecards",
            old_name="id_card_id",
            new_name="card",
        ),
        migrations.RenameField(
            model_name="ingamecards",
            old_name="id_game_id",
            new_name="game",
        ),
        migrations.RenameField(
            model_name="ingamecharactersheet",
            old_name="id_game_id",
            new_name="game",
        ),
        migrations.RenameField(
            model_name="ingameplayer",
            old_name="id_game_id",
            new_name="game",
        ),
        migrations.RenameField(
            model_name="ingameplayer",
            old_name="id_player_id",
            new_name="player",
        ),
    ]
