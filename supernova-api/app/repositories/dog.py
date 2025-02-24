from typing import Annotated

from fastapi import Depends

import app.core.database as db
from app.core.query_parser import QueryParser

query_parser = QueryParser(
    {
        "discrete": [
            "league_number",
        ]
    }
)


class DogRepository:
    def __init__(self):
        pass

    def get_dog(self, request, conn, param_dict, single):
        query_object = query_parser(request, param_dict)
        query = f"""
        SELECT
            league_number,
            dog_name,
            main_handler_id::text as main_handler_id,
            alternate_handler_id::text as alternate_handler_id,
            call_name,
            breed,
            height,
            jump_height,
            current_level_type_id::text as current_level_type_id,
            is_reactive,
            people,
            dogs,
            is_virtual
        FROM dog.dog
        WHERE 1 = 1 {query_object["query"]}
        """
        result_df = db.read_df(conn, query, query_object["params"], single=single)
        return result_df


DogRepositoryDep = Annotated[DogRepository, Depends()]
