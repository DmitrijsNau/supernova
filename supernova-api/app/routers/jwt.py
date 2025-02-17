# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.security import OAuth2PasswordRequestForm
# from typing import Annotated
# import jwt
# import uuid
# from datetime import datetime, timedelta

# from app.core.config import settings as s
# from app.core.authorization import NoAuth

# router: APIRouter = APIRouter(dependencies=[Depends(NoAuth)])

# # in the future this can be extended to allow more user to authenticate this way
# user = s["NEXUS_SERVICE_ACCOUNT_USER_NAME"]
# pwd = s["NEXUS_SERVICE_ACCOUNT_PASSWORD"]


# @router.post("/token")
# def signin_integration_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     user_name = form_data.username
#     user_password = form_data.password
#     if user_name == user:
#         if user_password == pwd:
#             token_obj = {s["VUE_APP_AZURE_AD_USER_KEY"]: user_name}
#             token_obj["iss"] = "FMNH"
#             token_obj["aud"] = s["VUE_APP_AZURE_AD_CLIENT_ID"]
#             token_obj["nbf"] = token_obj["iat"] = datetime.now().timestamp()
#             token_obj["exp"] = (datetime.now() + timedelta(minutes=60)).timestamp()
#             token_obj["uti"] = str(uuid.uuid4())
#             token_obj["provider"] = "FMNH"
#             token_obj["upn"] = user
#             idToken = jwt.encode(
#                 token_obj,
#                 s["FMNH_JWT_TOKEN_SECRET_KEY"],
#                 headers={"provider": "FMNH"},
#                 algorithm="HS256",
#             )
#             return {
#                 "access_token": idToken,
#                 "token_type": "bearer",
#                 "expires_in": 60 * 60,
#             }

#     raise HTTPException(status_code=403, detail="Invalid user name or password")
