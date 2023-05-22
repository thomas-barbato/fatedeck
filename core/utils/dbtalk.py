from ..models import (
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


class DBTalk:
    def __init__(self, db_table, **kwargs):
        self.db_table = db_table
        self.kwargs = kwargs
