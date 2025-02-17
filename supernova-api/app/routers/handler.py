# from fastapi import APIRouter, Depends, Request

# from app.core.authorization import JwtUserServiceDep
# from app.models.user import UserProfileModel, UserSettingModel, UserRoleModel
# from app.services.user import UserServiceDep

# router: APIRouter = APIRouter()


# @router.delete("")
# def delete_user(UserId: str, service: UserServiceDep):
#     return service.toggle_user_active(UserId, False)


# @router.get("/role")
# def get_role(request: Request, service: UserServiceDep, single=False):
#     return service.get_role(request, single)


# @router.get("/user-profile")
# def get_user_profile(request: Request, service: UserServiceDep, single=False):
#     return service.get_user_profile(request, single)


# @router.post("/user-profile")
# def post_user_profile(u: UserProfileModel, service: UserServiceDep):
#     return service.post_user_profile(u)


# @router.get("/user-role")
# def get_user_role(request: Request, service: UserServiceDep, single=False):
#     return service.get_user_role(request, single)


# @router.put("/user-role")
# def put_user_role(urm: UserRoleModel, service: UserServiceDep):
#     return service.put_user_role(urm)


# @router.get("/user-permission")
# def get_user_permission(request: Request, service: UserServiceDep):
#     return service.get_user_permission(request)


# @router.get("/user-setting")
# def get_user_setting(request: Request, service: UserServiceDep, single=True):
#     return service.get_user_setting(request, single)


# @router.post("/user-setting")
# def post_user_setting(u: UserSettingModel, service: UserServiceDep):
#     return service.post_user_setting(u)
