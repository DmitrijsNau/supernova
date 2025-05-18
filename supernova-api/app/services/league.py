from typing import Annotated
from fastapi import Depends

import app.core.database as db
from app.repositories.league import LeagueRepositoryDep
from app.models.league import EventModel, GameTypeModel, LevelModel, LevelTypeModel


class LeagueService:
    def __init__(
        self,
        repository: LeagueRepositoryDep,
        conn: db.LConnectionMainDep,
    ):
        self.repo = repository
        self.conn = conn

    def get_event(self, request, single):
        return db.df_to_json(self.repo.get_event(request, self.conn, None, single))

    def post_new_event(
        self,
        e: EventModel,
    ):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            # first create the new application
            dog_df = self.repo.post_new_event(self.conn, e)
            new_event: EventModel = EventModel(**dog_df)

            # finally prepare and return the result
            res = {"event": new_event.model_dump()}
            return res

    def get_game_type(self, request, single):
        return db.df_to_json(self.repo.get_game_type(request, self.conn, None, single))

    def post_new_game_type(
        self,
        g: GameTypeModel,
    ):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            # first create the new game type
            game_type_df = self.repo.post_new_game_type(self.conn, g)
            new_game_type: GameTypeModel = GameTypeModel(**game_type_df)

            # finally prepare and return the result
            res = {"game_type": new_game_type.model_dump()}
            return res

    def get_level(self, request, single):
        return db.df_to_json(self.repo.get_level(request, self.conn, None, single))

    def post_new_level(
        self,
        l: LevelModel,
    ):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            # first create the new level
            level_df = self.repo.post_new_level(self.conn, l)
            new_level: LevelModel = LevelModel(**level_df)

            # finally prepare and return the result
            res = {"level": new_level.model_dump()}
            return res

    def get_level_type(self, request, single):
        return db.df_to_json(self.repo.get_level_type(request, self.conn, None, single))

    def post_new_level_type(
        self,
        lt: LevelTypeModel,
    ):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            # first create the new level type
            level_type_df = self.repo.post_new_level_type(self.conn, lt)
            new_level_type: LevelTypeModel = LevelTypeModel(**level_type_df)

            # finally prepare and return the result
            res = {"level_type": new_level_type.model_dump()}
            return res


LeagueServiceDep = Annotated[LeagueService, Depends()]
