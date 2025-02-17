from pydantic import BaseModel
from typing import List


class UserProfileModel(BaseModel):
    UserId: str | None = None
    UserName: str
    UserDisplayName: str | None = None
    UserEmail: str | None = None
    UserTitle: str | None = None
    UserDepartment: str | None = None
    UserCompany: str | None = None

    def __post_init__(self):
        self.UserName = self.UserName.lower()
        self.UserDisplayName = (
            self.UserDisplayName.title() if self.UserDisplayName is not None else None
        )
        self.UserEmail = self.UserEmail.lower() if self.UserEmail is not None else None


class UserSettingModel(BaseModel):
    UserId: str
    Settings: str | None = None


class UserRoleModel(BaseModel):
    UserId: str
    RoleCodes: List[str]
