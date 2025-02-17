import json

from typing import Annotated
from fastapi import Depends

import app.core.database as db
from app.core.query_parser import QueryParser
from app.repositories.user import UserRepositoryDep
from app.models.user import UserRoleModel, UserSettingModel

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


class UserService:
    def __init__(
        self,
        repository: UserRepositoryDep,
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

    def get_user_profile(self, request, single):
        query_object = query_parser(request)
        with self.conn.begin():
            result_df = self.repo.get_user_profile(
                self.conn, query_object["query"], query_object["params"], single
            )
            return db.df_to_json(result_df)

    def post_user_profile(self, u):
        with db.begin_transaction_if_not_in_transaction(self.conn):
            user = self.repo.post_user_profile(self.conn, u)
            # when we have a new user, lets give them default user roles and settings
            if user["IsUserNew"]:
                self.repo.add_default_user_role(self.conn, user["UserId"])

                default_settings = self.repo.get_default_user_setting_for_user(
                    self.conn, user["UserId"]
                )
                self.repo.post_user_setting(
                    self.conn,
                    UserSettingModel(
                        UserId=user["UserId"], Settings=default_settings["Settings"]
                    ),
                )

            return db.df_to_json(user)

    def get_user_role(self, request, single):
        query_object = query_parser(request)
        with self.conn.begin():
            result_df = self.repo.get_user_role(
                self.conn, query_object["query"], query_object["params"], single
            )
            return db.df_to_json(result_df)

    def put_user_role(self, urm: UserRoleModel):
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

    def get_user_setting(self, request, single):
        query_object = query_parser(request)
        result_df = self.repo.get_user_setting(
            self.conn, query_object["query"], query_object["params"], single
        )
        return db.df_to_json(db.df_with_column_to_json(result_df, "Settings"))

    def post_user_setting(self, u):
        with self.conn.begin():
            return self.repo.post_user_setting(self.conn, u)


UserServiceDep = Annotated[UserService, Depends()]
