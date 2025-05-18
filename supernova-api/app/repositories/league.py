from typing import Annotated

from fastapi import Depends

import app.core.database as db
from app.core.query_parser import QueryParser
from app.models.league import EventModel, GameTypeModel, LevelModel, LevelTypeModel

query_parser = QueryParser(
    {"discrete": ["league_number", "level_type_id", "game_type_id", "event_id"]}
)


class LeagueRepository:
    def __init__(self):
        pass

    def get_event(self, request, conn, param_dict, single):
        query_object = query_parser(request, param_dict)
        query = f"""
        SELECT
            event_id::text as event_id,
            event_start_timestamp::text as event_start_timestamp,
            event_end_timestamp::text as event_end_timestamp,
            event_name
            FROM league.event
        WHERE 1 = 1 {query_object["query"]}
        """
        result_df = db.read_df(conn, query, query_object["params"], single=single)
        return result_df

    def post_new_event(self, conn, e: EventModel):
        query = """
        INSERT INTO league.event (event_name,
            event_start_timestamp,
            event_end_timestamp)
        VALUES (:event_name,
            :event_start_timestamp,
            :event_end_timestamp)
        RETURNING 
            event_id:: text as event_id,
            event_name,
            event_start_timestamp:: text as event_start_timestamp,
            event_end_timestamp:: text as event_end_timestamp;
        """
        res = db.read_df(
            conn,
            query,
            e.model_dump(),
            single=True,
        )
        return res

    def get_game_type(self, request, conn, param_dict, single):
        query_object = query_parser(request, param_dict)
        query = f"""
        SELECT
            game_type_id::text as game_type_id,
            game_name,
            game_description
            FROM league.game_type
        WHERE 1 = 1 {query_object["query"]}
        """
        result_df = db.read_df(conn, query, query_object["params"], single=single)
        return result_df

    def post_new_game_type(self, conn, g: GameTypeModel):
        query = """
        INSERT INTO league.game_type (game_name,
            game_description)
        VALUES (:game_name,
            :game_description)
        RETURNING 
            game_type_id,
            game_name,
            game_description;
        """
        res = db.read_df(
            conn,
            query,
            g.model_dump(),
            single=True,
        )
        return res

    def get_level(self, request, conn, param_dict, single):
        query_object = query_parser(request, param_dict)
        query = f"""
        SELECT
            level_id::text as level_id,
            league_number,
            level_type_id,
            game_type_id,
            event_id,
            heat_number,
            course,
            run_time_seconds,
            total_feet,
            is_qualified
            FROM league.level
        WHERE 1 = 1 {query_object["query"]}
        """
        result_df = db.read_df(conn, query, query_object["params"], single=single)
        return result_df

    def post_new_level(self, conn, l: LevelModel):
        query = """
        INSERT INTO league.level (league_number,
            level_type_id,
            game_type_id,
            event_id,
            heat_number,
            course,
            run_time_seconds,
            total_feet,
            is_qualified)
        VALUES (:league_number,
            :level_type_id,
            :game_type_id,
            :event_id,
            :heat_number,
            :course,
            :run_time_seconds,
            :total_feet,
            :is_qualified)
        RETURNING 
            level_id,
            league_number,
            level_type_id,
            game_type_id,
            event_id,
            heat_number,
            course,
            run_time_seconds,
            total_feet,
            is_qualified;
        """
        res = db.read_df(
            conn,
            query,
            l.model_dump(),
            single=True,
        )
        return res

    def get_level_type(self, request, conn, param_dict, single):
        query_object = query_parser(request, param_dict)
        query = f"""
        SELECT
            level_type_id::text as level_type_id,
            level_name,
            level_description
            FROM league.level_type
        WHERE 1 = 1 {query_object["query"]}
        """
        result_df = db.read_df(conn, query, query_object["params"], single=single)
        return result_df

    def post_new_level_type(self, conn, lt: LevelTypeModel):
        query = """
        INSERT INTO league.level_type (level_name,
            level_description)
        VALUES (:level_type_id,
            :level_name,
            :level_description)
        RETURNING 
            level_type_id,
            level_name,
            level_description;
        """
        res = db.read_df(
            conn,
            query,
            lt.model_dump(),
            single=True,
        )
        return res


LeagueRepositoryDep = Annotated[LeagueRepository, Depends()]
