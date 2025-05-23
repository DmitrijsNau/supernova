from fastapi import APIRouter, Depends, Request

from app.services.dog import DogServiceDep
from app.models.dog import DogModel

router: APIRouter = APIRouter()


@router.get("")
def get_dog(request: Request, service: DogServiceDep, single=False):
    return service.get_dog(request, single)


@router.post("")
def post_new_dog(d: DogModel, service: DogServiceDep):
    return service.post_new_dog(d)
