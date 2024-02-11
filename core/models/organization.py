from typing import Optional
from pydantic import BaseModel, Field
from quest_maker_api_shared_library.custom_types import PydanticObjectId


class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str]


class OrganizationUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class OrganizationResponse(BaseModel):
    id: PydanticObjectId = Field(alias='_id')
    name: str
    description: Optional[str]
    ownerId: PydanticObjectId = Field(alias='ownerId')
    createdAt: str
    updatedAt: str


class OrganizationInDB(BaseModel):
    name: str
    description: Optional[str]
    ownerId: PydanticObjectId = Field(alias='ownerId')
    createdAt: str
    updatedAt: str


class OrganizationOutDB(OrganizationInDB):
    pass


class OrganizationMemberInDB(BaseModel):
    organizationId: PydanticObjectId = Field(alias='organizationId')
    ownerId: PydanticObjectId = Field(alias='ownerId')
    memberId: PydanticObjectId = Field(alias='memberId')


class OrganizationMemberOutDB(OrganizationMemberInDB):
    id: PydanticObjectId = Field(alias='_id')
