from fastapi import APIRouter, Depends, Request

from app.services.league import LeagueServiceDep
from app.models.league import EventModel, GameTypeModel, LevelModel, LevelTypeModel

router: APIRouter = APIRouter()


@router.get("/event")
def get_event(request: Request, service: LeagueServiceDep, single=False):
    return service.get_event(request, single)


@router.post("/event")
def post_new_event(d: EventModel, service: LeagueServiceDep):
    return service.post_new_event(d)


@router.get("/game-type")
def get_game_type(request: Request, service: LeagueServiceDep, single=False):
    return service.get_game_type(request, single)


@router.post("/game-type")
def post_new_game_type(d: GameTypeModel, service: LeagueServiceDep):
    return service.post_new_game_type(d)


@router.get("/level")
def get_level(request: Request, service: LeagueServiceDep, single=False):
    return service.get_level(request, single)


@router.post("/level")
def post_new_level(d: LevelModel, service: LeagueServiceDep):
    return service.post_new_level(d)


@router.get("/level-type")
def get_level_type(request: Request, service: LeagueServiceDep, single=False):
    return service.get_level_type(request, single)


@router.post("/level-type")
def post_new_level_type(d: LevelTypeModel, service: LeagueServiceDep):
    return service.post_new_level_type(d)
