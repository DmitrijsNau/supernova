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
        return self.repo.get_dog(request, self.conn, single)


DogServiceDep = Annotated[DogService, Depends()]
