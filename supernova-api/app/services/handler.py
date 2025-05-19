from typing import Annotated
from fastapi import Depends

import app.core.database as db
from app.core.query_parser import QueryParser
from app.repositories.handler import HandlerRepositoryDep
from app.models.handler import HandlerModel

query_parser = QueryParser(
    {
        "discrete": [
            "UserId",
            "UserName",
            "UserDisplayName",
            "UserEmail",
            "UserTitle",
            "UserDepartment",
            "UserCompany",
            "IsUserActive",
            "RoleCode",
        ]
    }
)


class HandlerService:
    def __init__(
        self,
        repository: HandlerRepositoryDep,
        conn: db.LConnectionMainDep,
    ):
        self.repo = repository
        self.conn = conn

    def get_role(self, request, single):
        query_object = query_parser(request)
        with self.conn.begin():
            result_df = self.repo.get_role(
                self.conn, query_object["query"], query_object["params"], single
            )
            return db.df_to_json(result_df)

    def toggle_user_active(self, UserId, isUserActive):
        with self.conn.begin():
            result_df = self.repo.toggle_user_active(self.conn, UserId, isUserActive)
            return db.df_to_json(result_df)

    def get_handler(self, request, single):
        query_object = query_parser(request)
        with self.conn.begin():
            result_df = self.repo.get_handler(
                self.conn, query_object["query"], query_object["params"], single
            )
            return db.df_to_json(result_df)

    def post_handler(self, u):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            user = self.repo.post_handler(self.conn, u)
            return db.df_to_json(user)

    def get_user_role(self, request, single):
        query_object = query_parser(request)
        with self.conn.begin():
            result_df = self.repo.get_user_role(
                self.conn, query_object["query"], query_object["params"], single
            )
            return db.df_to_json(result_df)

    def put_user_role(self, urm: HandlerModel):
        with self.conn.begin():
            user_role_dicts = list(
                map(lambda x: {"UserId": urm.UserId, "RoleCode": x}, urm.RoleCodes)
            )
            self.repo.put_user_role(self.conn, user_role_dicts)

    def get_user_permission(self, request):
        query_object = query_parser(request)
        with self.conn.begin():
            result_df = self.repo.get_user_permission(
                self.conn, query_object["query"], query_object["params"]
            )
            return db.df_to_json(result_df)


HandlerServiceDep = Annotated[HandlerService, Depends()]
