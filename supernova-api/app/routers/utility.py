import asyncio
from time import sleep

from fastapi import APIRouter, Body, Depends, Request

import app.core.database as db

router: APIRouter = APIRouter()
# empty array means no dependencies
dependencies = []


@router.get("/test-api")
def test_api():
    return "API online"


@router.get("/test-main-sql")
def test_main_sql(conn=Depends(db.LConnectionMain)):
    query = """
    SELECT 1 as [status]
    """
    try:
        res = db.read_df(conn, query, single=True)
        assert res["status"] == 1
        return "Database online"
    except Exception as e:
        return e
