# from datetime import datetime
# from typing import Annotated, Any

# import jwt
# from fastapi import Depends, HTTPException, Request
# from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# import app.core.database as db
# from app.core.config import settings as s
# from app.core.logger import logger

# clientConf = {
#     "azure_ad_app_id": s["VUE_APP_AZURE_AD_CLIENT_ID"],
#     "azure_ad_issuer": f"https://login.microsoftonline.com/{s['VUE_APP_AZURE_AD_TENANT_ID']}/v2.0",
#     "azure_ad_jwks_uri": "https://login.microsoftonline.com/common/discovery/keys",
# }

# user_key = s["VUE_APP_AZURE_AD_USER_KEY"]


# # Utility class that can be used as a dependency to indicate something does not need authentication
# class NoAuth:
#     def __call__(self):
#         return True


# class JWTBearer(HTTPBearer):
#     def __init__(self, auto_error: bool = True):
#         super(JWTBearer, self).__init__(auto_error=auto_error)

#     async def __call__(self, request: Request):
#         credentials: HTTPAuthorizationCredentials = await super(
#             JWTBearer, self
#         ).__call__(request)
#         if credentials:
#             if not credentials.scheme == "Bearer":
#                 raise HTTPException(
#                     status_code=403, detail="Invalid authentication scheme."
#                 )
#             payload = self.verify_jwt(credentials.credentials)
#             if "Exception" in payload:
#                 raise HTTPException(status_code=403, detail=payload["Message"])
#             return payload
#         else:
#             raise HTTPException(
#                 status_code=403, detail="Invalid authorization code."
#             )

#     def verify_jwt(self, jwttoken: str) -> Any:
#         try:
#             if self._is_provider_fmnh(jwttoken):
#                 return self._verify_fmnh(jwttoken)
#             if self._is_provider_msal(jwttoken):
#                 return self._verify_msal(jwttoken)
#             else:
#                 raise "Unable to determine jwt provider"
#         except Exception as e:
#             payload = {"Exception": True, "Message": str(e)}
#         return payload

#     def _is_provider_msal(self, jwttoken):
#         headers = jwt.get_unverified_header(jwttoken)
#         if "provider" in headers and headers["provider"] == "FMNH":
#             return False
#         else:
#             return True

#     def _is_provider_fmnh(self, jwttoken):
#         headers = jwt.get_unverified_header(jwttoken)
#         return "provider" in headers and headers["provider"] == "FMNH"

#     def _verify_msal(self, jwttoken):
#         return verify_jwt(
#             token=jwttoken,
#             valid_audiences=[clientConf["azure_ad_app_id"]],
#             issuer=clientConf["azure_ad_issuer"],
#             jwks_uri=clientConf["azure_ad_jwks_uri"],
#             verify=True,
#         )

#     def _verify_fmnh(self, jwttoken):
#         try:
#             decoded = jwt.decode(
#                 jwttoken,
#                 s["FMNH_JWT_TOKEN_SECRET_KEY"],
#                 verify=True,
#                 algorithms=["HS256"],
#                 audience=[clientConf["azure_ad_app_id"]],
#                 issuer="FMNH",
#             )
#         except jwt.exceptions.PyJWTError:
#             raise "Invalid JWT token"
#         else:
#             return decoded


# JwtUserService = JWTBearer()
# JwtUserServiceDep = Annotated[JWTBearer, Depends(JwtUserService)]


# def get_user_obj(request: Request, User=Depends(JwtUserService)):
#     user_obj = request.app.state.users.get(User[user_key])
#     return user_obj


# def get_user_id(user=Depends(get_user_obj)):
#     return user["UserId"]


# class UserHasPermission(object):
#     def __init__(self, permission):
#         self.permission = permission

#     def __call__(self, request: Request, user: JwtUserServiceDep):
#         print(user)
#         permissions_from_db = request.app.state.permissions.get(
#             user[user_key], []
#         )
#         permissions_from_ad = user.get("roles", [])
#         permissions = list(set(permissions_from_db + permissions_from_ad))
#         logger.info(
#             f"{user[user_key]} - {len(permissions)} Permissions - {', '.join(permissions)}"
#         )
#         if self.permission in permissions:
#             logger.info(f"User has {self.permission} permission")
#             return None
#         else:
#             logger.error(f"User rejected - No {self.permission} permission")
#             raise HTTPException(
#                 status_code=403,
#                 detail=f"You need {self.permission} permission",
#             )
