from typing import Annotated

from fastapi import Depends

import app.core.database as db
from app.core.query_parser import TableValueConstructor
from app.models.handler import HandlerModel


class HandlerRepository:
    def __init__(self):
        pass

    def get_handler(self, conn, filter_query, filter_params, single):
        query = f"""
        SELECT handler_id::text as handler_id,
        league_number,
        handler_name,
        handler_email,
        handler_role,
        is_handler_active
        from handler.handler
        where 1 = 1 {filter_query};
        """
        parameters = filter_params
        result_df = db.read_df(conn, query, parameters, single=single)
        return result_df

    def toggle_user_active(self, conn, UserId, IsUserActive):
        query = """
        UPDATE [handler].[handler]
        SET [is_handler_active] = :is_handler_active
        OUTPUT [inserted].*
        WHERE [UserId] = :UserId
        """
        params = {"UserId": UserId, "is_handler_active": IsUserActive}
        result_df = db.read_df(conn, query, params)
        return result_df

    def post_handler(self, conn, u):
        query = """
        INSERT INTO handler.handler (
            handler_id,
            league_number,
            handler_name,
            handler_email,
            handler_role,
            is_handler_active
        )
        VALUES (
            :handler_id,
            :league_number,
            :handler_name,
            :handler_email,
            :handler_role,
            TRUE
        )
        RETURNING 
            handler_id::text as handler_id,
            league_number,
            handler_name,
            handler_email,
            handler_role,
            is_handler_active;
        """
        res = db.read_df(conn, query, u.model_dump(), single=True)
        return res

    def get_user_role(self, conn, filter_query, filter_params, single):
        query = f"""
        select *
        from [user].[vw_UserRole]
        where 1 = 1 {filter_query};
        """
        parameters = filter_params
        result_df = db.read_df(conn, query, parameters, single=single)
        return result_df

    def put_user_role(self, conn, roles):
        tvc = TableValueConstructor(["UserId", "RoleCode"], roles)
        query = f"""
        WITH [Source] AS (
            SELECT [UserId], [RoleCode]
            FROM (VALUES {tvc.row_value_expression()}) AS [Source] ([UserId], [RoleCode])
            )
            MERGE [user].[UserRole] AS [Target]
        USING [Source]
        ON [Source].[UserId] = [Target].[UserId] AND [Source].[RoleCode] = [Target].[RoleCode]
        WHEN NOT MATCHED BY SOURCE AND [Target].[UserId] IN (SELECT [source].[UserId]
                                                            FROM [Source]) THEN DELETE
        WHEN NOT MATCHED BY TARGET THEN
            INSERT ([UserId], [RoleCode], [IsUserRoleActive])
            VALUES ([Source].[UserId], [Source].[RoleCode], 1);
        """
        db.exec_sql(conn, query, tvc.row_value_parameter())
        return None

    def add_default_user_role(self, conn, user_id):
        query = f"""
        INSERT INTO [user].[UserRole]([UserId], [RoleCode], [IsUserRoleActive])
        SELECT :UserId, [RoleCode], 1
        FROM [user].[Role]
        WHERE [IsRoleActive] = 1
        AND [IsRoleDefaultToAllUsers] = 1
        """
        db.exec_sql(conn, query, {"UserId": user_id})

    def get_user_permission(self, conn, filter_query, filter_params):
        query = f"""
        select *
        from [user].[vw_UserRolePermission]
        where 1 = 1 {filter_query};
        """
        parameters = filter_params
        result_df = db.read_df(conn, query, parameters)
        return result_df

    def get_user_setting(self, conn, filter_query, filter_params, single):
        query = f"""
        select *
        from [user].[vw_UserSetting]
        where 1 = 1 {filter_query};
        """
        parameters = filter_params
        result_df = db.read_df(conn, query, parameters, single=single)
        return result_df

    def get_default_user_setting(self, conn, filter_query, filter_params, single=False):
        query = f"""
        SELECT *
        FROM [user].[DefaultUserSetting]
        WHERE 1 = 1 {filter_query}
        """
        result_df = db.read_df(conn, query, filter_params, single)
        return result_df

    def get_default_user_setting_for_user(self, conn, UserId: str):
        query = f"""
        SELECT *
        FROM [user].[DefaultUserSetting]
        WHERE [RoleCode] = (SELECT TOP 1 [RoleCode] FROM [user].[UserRole] WHERE [UserId] = :UserId)
        """
        result_df = db.read_df(conn, query, {"UserId": UserId}, single=True)
        return result_df

    def post_user_setting(self, conn, u: HandlerModel):
        query = """
        UPDATE [US] WITH (UPDLOCK, SERIALIZABLE)
        SET [Settings] = :Settings
        FROM [user].[User] [U]
                JOIN [user].[UserSetting] [US] ON [U].[UserId] = [US].[UserId]
        WHERE [U].[UserId] = :UserId
        AND [U].[IsUserActive] = 1;
        IF @@ROWCOUNT = 0
            BEGIN
                INSERT INTO [user].[UserSetting]([UserId], [Settings])
                SELECT [U].[UserId], :Settings
                FROM [user].[User] [U]
                WHERE [U].[UserId] = :UserId
                AND [U].[IsUserActive] = 1;
            END
        """
        db.exec_sql(conn, query, u.model_dump())
        return u


HandlerRepositoryDep = Annotated[HandlerRepository, Depends()]
