from typing import Annotated

from fastapi import Depends

import app.core.database as db


class DogRepository:
    def __init__(self):
        pass

    def get_dog(self, request, conn, single):
        query = f"""
        SELECT t.*
        FROM dog.dog t
        """
        result_df = db.read_df(conn, query, None, single=single)
        return result_df


DogRepositoryDep = Annotated[DogRepository, Depends()]
