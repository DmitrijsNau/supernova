from importlib import import_module
from pkgutil import iter_modules

from fastapi import Depends

import app.routers as routers
from app.core.config import settings as s
from app.core.logger import logger


def bind_routers(app):
    """
    Load all router files defined in the routers folder to the app.

    Each file must have a router property exposing an APIRouter object.
    Additionaly, prefix and tags properties may also be included to
    specify the path and the route group to be displayed in OpenAPI (swagger) page
    """
    for _, name, _ in iter_modules(routers.__path__):
        router_module = import_module(f"app.routers.{name}")

        try:
            router_obj = router_module.router
            route_name = name.replace("_", "-")
            tag_name = name.replace("_", " ").title()
            # look for prefix in the file, it not, use the route_name
            prefix = (
                getattr(router_obj, "prefix", lambda: None) or f"/{route_name}"
            )
            tags = getattr(router_obj, "tags", lambda: None) or [tag_name]
            # if s["PYTHON_ENV"] != "local_development":
            #     dependencies = getattr(
            #         router_obj, "dependencies", lambda: None
            #     ) or [Depends(JwtUserService)]
            # else:
            logger.info("Local Development Mode, No Authentication")
            dependencies = []
            print(f"Loading Router {route_name}")
            app.include_router(
                router_obj,
                prefix=prefix,
                tags=tags,
                dependencies=dependencies,
            )
            logger.info(f"Auto-bind router: {route_name}")
        except Exception as e:
            print(e)
            logger.error(f"Cannot load router '{route_name}'")
            logger.error(e)
