from typing import List, Optional
from pydantic import BaseModel, Field
from quest_maker_api_shared_library.custom_types import PydanticObjectId


class RoleCreate(BaseModel):
    name: str
    organizationId: PydanticObjectId = Field(alias='organizationId')
    description: Optional[str]
    permissions: List[str] = []
    createdAt: str
    updatedAt: str


class RoleUpdate(RoleCreate):
    pass


class RoleResponse(RoleCreate):
    id: PydanticObjectId = Field(alias='_id')


class RoleInDB(RoleCreate):
    pass


class RoleOutDB(RoleResponse):
    pass


class RoleAssignedInDB(BaseModel):
    toId: PydanticObjectId = Field(alias='toId')
    organizationId: PydanticObjectId = Field(alias='organizationId')
    roleId: PydanticObjectId = Field(alias='roleId')


class RoleAssignedOutDB(RoleAssignedInDB):
    id: PydanticObjectId = Field(alias='_id')
