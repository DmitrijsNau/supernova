import json

from typing import Annotated
from fastapi import Depends

import app.core.database as db
from app.repositories.dog import DogRepositoryDep
from app.models.dog import DogModel


class DogService:
    def __init__(
        self,
        repository: DogRepositoryDep,
        conn: db.LConnectionMainDep,
    ):
        self.repo = repository
        self.conn = conn

    def get_dog(self, request, single):
        return db.df_to_json(self.repo.get_dog(request, self.conn, None, single))

    def post_new_dog(
        self,
        d: DogModel,
    ):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            # first create the new application
            dog_df = self.repo.post_new_dog(self.conn, d)
            new_dog: DogModel = DogModel(**dog_df)

            # finally prepare and return the result
            res = {"dog": new_dog.model_dump()}
            return res


DogServiceDep = Annotated[DogService, Depends()]
