from concurrent.futures.process import ProcessPoolExecutor
from concurrent.futures.thread import ThreadPoolExecutor

import gunicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_restful.tasks import repeat_every
from starlette.responses import JSONResponse

import app.core.database as db
from app.core.database import main_engine
from app.core.logger import logger
from app.core.router_setup import bind_routers

# create the main app, with or without the root path
app: FastAPI = FastAPI(default_response_class=ORJSONResponse)
# app: FastAPI = FastAPI(root_path="/api/v1")

# cors
origins = [
    "http://localhost:9000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def error_exception_handler(request: Request, exc: Exception):
    print(str(exc))
    response = JSONResponse(content={"message": str(exc)}, status_code=500)
    # Since the CORSMiddleware is not executed when an unhandled server exception
    # occurs, we need to manually set the CORS headers ourselves if we want the FE
    # to receive a proper JSON 500, opposed to a CORS error.
    # Setting CORS headers on server errors is a bit of a philosophical topic of
    # discussion in many frameworks, and it is currently not handled in FastAPI.
    # See dotnet core for a recent discussion, where ultimately it was
    # decided to return CORS headers on server failures:
    # https://github.com/dotnet/aspnetcore/issues/2378
    origin = request.headers.get("origin")
    if origin:
        # Have the middleware do the heavy lifting for us to parse
        # all the config, then update our response headers
        cors = CORSMiddleware(
            app=app,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Logic directly from Starlette's CORSMiddleware:
        # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

        response.headers.update(cors.simple_headers)
        has_cookie = "cookie" in request.headers

        # If request includes any cookie headers, then we must respond
        # with the specific origin instead of '*'.
        if cors.allow_all_origins and has_cookie:
            response.headers["Access-Control-Allow-Origin"] = origin

        # If we only allow specific origins, then we have to mirror back
        # the Origin header in the response.
        elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add_vary_header("Origin")

    return response


# include auto routers
bind_routers(app)


# initial setup
@app.on_event("startup")
async def create_thread_pool_executor():
    app.state.executor = ThreadPoolExecutor(max_workers=8)
    app.state.process_executor = ProcessPoolExecutor(max_workers=4)
    app.state.main_engine = main_engine


@app.on_event("shutdown")
async def shutdown_thread_pool_executor():
    app.state.executor.shutdown()
    app.state.process_executor.shutdown()
    app.state.main_engine.dispose()


# # initial setup
# @app.on_event("startup")
# @repeat_every(seconds=30, logger=logger)  # increase the seconds value
# async def load_all_user_permissions():
#     with db.main_engine.connect() as conn:
#         with conn.begin():
#             query = """
#             select *
#             from [user].[vw_UserRolePermission]
#             where [IsUserActive] = 1
#             """
#             result_df = db.read_df(conn, query)
#     app.state.permissions = (
#         result_df.groupby("UserName")["UserPermissionCode"].agg(list).to_dict()
#     )


# # initial setup
# @app.on_event("startup")
# @repeat_every(seconds=30, logger=logger)  # increase the seconds value
# async def load_all_user():
#     with db.main_engine.connect() as conn:
#         with conn.begin():
#             query = """
#             select *
#             from [user].[vw_User]
#             where [IsUserActive] = 1
#             """
#             result_df = db.read_df(conn, query)
#     app.state.users = result_df.set_index("UserName").to_dict(orient="index")


# # initial setup
# @app.on_event("startup")
# @repeat_every(seconds=30, logger=logger)  # increase the seconds value
# async def load_app_status():
#     with db.main_engine.connect() as conn:
#         with conn.begin():
#             query = """
#             select *
#             from [dbo].[AppStatus] [AS]
#             """
#             result_df = db.read_df(conn, query)
#     app.state.app_status = db.json_encode(
#         {
#             app_name: db.df_to_json(group.iloc[0])
#             for app_name, group in result_df.groupby("AppName")
#         }
#     )


if __name__ == "__main__":
    gunicorn.run(app, host="0.0.0.0", port=8000, debug=True, reload=True)
