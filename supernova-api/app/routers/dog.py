from fastapi import APIRouter, Depends, Request

from app.services.dog import DogServiceDep

router: APIRouter = APIRouter()


@router.get("")
def get_dog(request: Request, service: DogServiceDep, single=False):
    return service.get_dog(request, single)
