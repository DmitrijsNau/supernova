from fastapi import APIRouter, Depends, Request

# from app.core.authorization import JwtUserServiceDep
from app.models.handler import HandlerModel
from app.services.handler import HandlerServiceDep

router: APIRouter = APIRouter()


@router.delete("")
def delete_user(handler_id: str, service: HandlerServiceDep):
    return service.toggle_handler_active(handler_id, False)


@router.get("/role")
def get_role(request: Request, service: HandlerServiceDep, single=False):
    return service.get_role(request, single)


@router.get("/user-profile")
def get_user_profile(request: Request, service: HandlerServiceDep, single=False):
    return service.get_user_profile(request, single)


@router.post("/")
def post_handler(u: HandlerModel, service: HandlerServiceDep):
    return service.post_handler(u)


@router.get("/user-role")
def get_user_role(request: Request, service: HandlerServiceDep, single=False):
    return service.get_user_role(request, single)
