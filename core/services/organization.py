from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from quest_maker_api_shared_library.custom_types import PydanticObjectId


from core.config.env import Env
from core.config.database import OrganizationDatabase
from core.models.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate, OrganizationInDB
from core.errors.database import DocumentNotFoundError

env = Env()
db = OrganizationDatabase()


class OrganizationService:
    def create(self, owner_id: PydanticObjectId, data: OrganizationCreate) -> PydanticObjectId:
        try:
            # Load data into OrganizationInDB container
            organization = OrganizationInDB(
                name=data.name,
                description=data.description,
                ownerId=str(owner_id),
                memberId=str(owner_id),
                createdAt=str(datetime.utcnow()),
                updatedAt=str(datetime.utcnow())
            )

            # Convert the OrganizationInDB container into a dict
            organization_dict = organization.model_dump()

            # Create new organization instance in database collection
            document = db.organization_collection.insert_one(organization_dict)

            return str(document.inserted_id)

        except Exception as e:
            raise e

    def read(self, owner_id: Optional[PydanticObjectId], member_id: Optional[PydanticObjectId], organization_id: PydanticObjectId) -> OrganizationResponse:
        try:
            if owner_id:
                document = db.organization_collection.find_one(
                    {'_id': ObjectId(organization_id), 'ownerId': ObjectId(owner_id)})
            if member_id:
                document = db.organization_collection.find_one(
                    {'_id': ObjectId(organization_id), 'memberId': ObjectId(member_id)})
            if document is None:
                raise DocumentNotFoundError
            # Convert ObjectId's to strings
            document['_id'] = str(document['_id'])
            document['ownerId'] = str(document['ownerId'])
            document['memberId'] = str(document['memberId'])
            return document
        except Exception as e:
            raise e

    def read_all(self, member_id: PydanticObjectId) -> List[OrganizationResponse]:
        try:
            documents = db.organization_collection.find(
                {'memberId': ObjectId(member_id)})
            result = []

            if documents is None:
                raise DocumentNotFoundError
            for document in documents:
                # Load result into OrganizationResponse container
                document = OrganizationResponse(
                    _id=str(document['_id']),
                    name=document['name'],
                    description=document['description'],
                    ownerId=str(document['ownerId']),
                    memberId=str(document['memberId']),
                    createdAt=document['createdAt'],
                    updatedAt=document['updatedAt']
                )
                result.append(document)
            return result

        except Exception as e:
            raise e

    def update(self, owner_id: PydanticObjectId, organization_id: PydanticObjectId, data: Union[OrganizationUpdate, Dict[str, Any]]):
        try:
            if isinstance(data, OrganizationUpdate):
                data = data.model_dump(exclude_unset=True)

            # Update and convert date in updatedAt field to string
            data['updatedAt'] = str(datetime.utcnow())
            # Find and update an organization instance
            db.organization_collection.update_one(
                {'_id': ObjectId(organization_id), 'ownerId': ObjectId(owner_id)}, {'$set': data})
        except Exception as e:
            raise e

    def delete(self, owner_id: PydanticObjectId, organization_id: PydanticObjectId):
        try:
            # Delete an organization instance using it's id and owner_id
            db.organization_collection.delete_one(
                {"_id": ObjectId(organization_id), 'ownerId': ObjectId(owner_id)})
        except Exception as e:
            raise e
