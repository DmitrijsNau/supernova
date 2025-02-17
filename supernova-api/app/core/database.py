import json
import time
import pg8000

from collections.abc import Iterable
from typing import Annotated, Dict, Optional
from contextlib import contextmanager, nullcontext
import orjson
import pandas as pd
from fastapi import Depends
from sqlalchemy import bindparam, create_engine
from sqlalchemy.engine import URL, Connection, Engine
from sqlalchemy.sql import text

from app.core.config import settings as s
from app.core.logger import logger

"""
Start the database part
"""


def generate_database_url(dbSettings):
    url = URL.create(
        drivername="postgresql+psycopg2",
        host=dbSettings["server"],
        database=dbSettings["database"],
        username=dbSettings["uid"],
        password=dbSettings["pwd"],
        port=dbSettings["port"],
    )
    return url


DbSettings = {
    "main": {
        "server": s["MAIN_DB_SERVER"],
        "database": s["MAIN_DB_NAME"],
        "uid": s["MAIN_DB_USER"],
        "pwd": s["MAIN_DB_PWD"],
        "port": s["MAIN_DB_PORT"],
        "url_generator": generate_database_url,
    },
    "maindbo": {
        "server": s["MAIN_DB_DBO_SERVER"],
        "database": s["MAIN_DB_DBO_NAME"],
        "uid": s["MAIN_DB_DBO_USER"],
        "pwd": s["MAIN_DB_DBO_PWD"],
        "port": s["MAIN_DB_DBO_PORT"],
        "url_generator": generate_database_url,
    },
}

# create engine
engine: Dict[str, Engine] = {
    k: create_engine(
        url=v["url_generator"](v),
        max_overflow=16,
        pool_pre_ping=True,
        pool_size=8,
        pool_recycle=1800,
        echo=s["ECHO"] == "TRUE",
        isolation_level="READ COMMITTED",
    )
    for k, v in DbSettings.items()
}


# create the connection, we need to parameterize the connection
# usage, initialize first, then use as dependency
class LConnection:
    def __init__(self, dbname: str):
        self.dbname = dbname
        self.db_engine = engine[dbname]

    def __call__(self):
        # sometimes the conn is none, no idea why, but we can check here
        # try to see if the connection is valid
        n_retries = 3
        for _ in range(n_retries):
            try:
                conn: Connection = self.db_engine.connect()
                break
            except:
                logger.exception(f"DB Connection Fail {self.dbname}")
                time.sleep(1)
                continue
        try:
            yield conn
        except:
            if conn.in_transaction():
                conn.rollback()
        finally:
            conn.close()


# used by main.py
main_engine_name = "maindbo"
main_engine = engine[main_engine_name]


def LConnectionMain():
    lc = LConnection(main_engine_name)
    yield from lc()


LConnectionMainDep = Annotated[Connection, Depends(LConnectionMain)]

"""
Start the CURD part
"""


def read_df(
    connection: Connection,
    query: str,
    params: Optional[dict] = None,
    single: Optional[bool] = False,
) -> pd.DataFrame:
    # extra things to check after migrating to sqlalchemy 2.0
    # we want to check if the connection coming in is in a transaction
    # if it is, means someone out there is handling it
    # if it is not, means that whoever reads the data needs to close the transaction
    is_in_transaction = connection.in_transaction()
    if not is_in_transaction:
        connection.begin()
    try:
        query_text = text(query)
        # handles the "in" style where statements
        if params is not None:
            for param in params:
                if isinstance(params[param], list):
                    query_text = query_text.bindparams(
                        bindparam(param, expanding=True)
                    )

        data: pd.DataFrame = pd.read_sql_query(
            query_text, connection, params=params
        )
        if not is_in_transaction:
            connection.commit()
        if single:
            if len(data) >= 1:
                return data.iloc[0]
            else:
                return pd.Series([])
        else:
            return data
    except Exception as e:
        if not is_in_transaction:
            connection.rollback()
        raise e


def df_to_json(df):
    if isinstance(df, pd.DataFrame):
        return json.loads(df.to_json(orient="records", date_format="iso"))
    if isinstance(df, dict):
        return df
    else:
        return json.loads(df.to_json(orient="columns", date_format="iso"))


def df_with_column_to_json(df, column_name=None):
    if column_name and not df.empty:
        if isinstance(df, pd.DataFrame):
            df[column_name] = df[column_name].apply(json.loads)
        else:
            df[column_name] = json.loads(df[column_name])
    return df


"""
default for json_encode class
"""


def default(obj):
    if isinstance(obj, pd.Timestamp):
        return obj.strftime()
    raise TypeError


def json_encode(d):
    return orjson.loads(
        orjson.dumps(d, option=orjson.OPT_SERIALIZE_NUMPY, default=default)
    )


def write_df(
    connection: Connection, df, dtname, schema="dbo", if_exists="append"
):
    is_in_transaction = connection.in_transaction()
    if not is_in_transaction:
        connection.begin()
    try:
        n_columns = len(df.columns)
        chunksize = 2009 // n_columns
        df.to_sql(
            dtname,
            con=connection,
            schema=schema,
            index=False,
            if_exists=if_exists,
            method="multi",
            chunksize=chunksize,
        )
        if not is_in_transaction:
            connection.commit()
    except Exception as error:
        if not is_in_transaction:
            connection.rollback()
        raise error


def exec_sql(connection: Connection, query: str, params: dict = {}):
    is_in_transaction = connection.in_transaction()
    if not is_in_transaction:
        connection.begin()
    try:
        query_text = text(query)
        rs = connection.execute(query_text, params)
        if not is_in_transaction:
            connection.commit()
        return rs
    except Exception as error:
        if not is_in_transaction:
            connection.rollback()
        raise error


def flatten(xs):
    for x in xs:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        else:
            yield x


def exec_raw_sql(connection: Connection, query: str, params: list = []):
    logger.info(f"Executing {query}")
    is_in_transaction = connection.in_transaction()
    if not is_in_transaction:
        connection.begin()
    try:
        results = []
        non_results = []
        with connection.connection.cursor() as cursor:
            cursor.execute(query, *params)
            # now we parse the cursor Naien's way
            while True:
                try:
                    result = cursor.fetchall()
                    results.append(result)
                    logger.info(f"Result Set - {len(result)} Rows")
                except:
                    message = " ".join(flatten(cursor.messages))
                    row_count = cursor.rowcount
                    if message == "":
                        info = f"Row Count ({row_count})"
                    else:
                        info = message + " - " + f"Row Count ({row_count})"
                    non_result = {
                        "messages": message,
                        "rowcount": row_count,
                        "info": info,
                    }
                    non_results.append(non_result)
                    logger.info(f"Non-result Set - {info}")
                if not cursor.nextset():
                    break
            return {"results": results, "non_results": non_results}
    except Exception as error:
        if not is_in_transaction:
            connection.rollback()
        raise error


"""
utility for begining transactions conditionally
"""


@contextmanager
def begin_transaction_if_not_in_transaction(connection):
    """
    Context manager that starts a transaction only if one isn't already in progress.

    Args:
        connection: Database connection object with begin() method and in_transaction() check
    """
    with (
        connection.begin()
        if not connection.in_transaction()
        else nullcontext()
    ):
        yield
