from datetime import datetime
from logging import log
from typing import Any, Dict, List, Optional, Union

from bson import ObjectId
from pymongo.errors import DuplicateKeyError as MongoDBDuplicateKeyError
from quest_maker_api_shared_library.custom_types import PydanticObjectId
from quest_maker_api_shared_library.errors.database import DuplicateKeyError

from core.models.roles import RoleAssignedInDB, RoleCreate, RoleInDB, RoleResponse
from core.config.env import Env
from core.config.database import OrganizationDatabase
from core.utils.permissions import Permissions

env = Env()
db = OrganizationDatabase()


class DefaultRoles:
    admin = 'admin'
    manager = 'manager'
    user = 'user'

    @classmethod
    def __iter__(cls):
        return iter([cls.admin, cls.manager, cls.user])


class RoleManager:
    def setup(self, organization_id: PydanticObjectId):
        role_ids = []
        try:
            exists = db.role_collection.count_documents(
                {'name': {'$in': [role for role in DefaultRoles()]}})

            if exists == 0:
                admin = {'name': 'admin', 'organizationId': ObjectId(organization_id), 'description': "Admin role", 'permissions': [
                    permission for permission in Permissions()], 'createdAt': str(datetime.utcnow()), 'updatedAt': str(datetime.utcnow())}
                manager = {'name': 'manager', 'organizationId': ObjectId(organization_id), 'description': "Manager role", 'permissions': [Permissions.read_own, Permissions.write_own, Permissions.delete_own,
                                                                                                                                          Permissions.read_all, Permissions.write_all, Permissions.delete_all,
                                                                                                                                          Permissions.read_org, Permissions.write_org, Permissions.delete_org,
                                                                                                                                          Permissions.access_control], 'createdAt': str(datetime.utcnow()), 'updatedAt': str(datetime.utcnow())}
                user = {'name': 'user', 'organizationId': ObjectId(organization_id), 'description': "User role", 'permissions': [
                    Permissions.read_own, Permissions.write_own, Permissions.delete_own], 'createdAt': str(datetime.utcnow()), 'updatedAt': str(datetime.utcnow())}
                documents = db.role_collection.insert_many(
                    [admin, manager, user])
                for id in documents.inserted_ids:
                    role_ids.append(id)
                return role_ids
        except Exception as e:
            raise e

    def create(self, data: RoleCreate):
        try:
            # Load data into RoleInDB container
            role = RoleInDB(
                name=data.name,
                organization_id=str(data.organization_id),
                description=data.description,
                permissions=data.permissions,
                createdAt=str(datetime.utcnow()),
                updatedAt=str(datetime.utcnow())
            )

            # Convert the RoleInDB container into a dictionary
            role_dict = role.model_dump()

            # Create new role instance in database collection
            db.role_collection.insert_one(role_dict)
        except Exception as e:
            raise e

    def get_roles(self, to_id: PydanticObjectId) -> Optional[List[RoleResponse]]:
        roles = []
        try:
            role_assigned_documents = db.role_assigned.find(
                {'toId': ObjectId(to_id)})
            # role_assigned_documents = db.role_assigned.find({'toId': to_id})
            for role_assigned_document in role_assigned_documents:
                roles.append(db.role_collection.find_one(
                    {'_id': role_assigned_document['roleId']}))
            for role in roles:
                role = RoleResponse(
                    _id=str(role['_id']),
                    name=role['name'],
                    description=role['description'],
                    organizationId=str(role['organizationId']),
                    permissions=role['permissions'],
                    createdAt=role['createdAt'],
                    updatedAt=role['updatedAt']
                )
            return roles
        except Exception as e:
            raise e

    def assign_role(self, data: RoleAssignedInDB):
        try:
            if isinstance(data, RoleAssignedInDB):
                data = data.model_dump()
            data['toId'] = ObjectId(data['toId'])
            data['organizationId'] = ObjectId(data['organizationId'])
            data['roleId'] = ObjectId(data['roleId'])

            db.role_assigned.insert_one(data)
        except Exception as e:
            raise e

    def revoke_role(self, role_id: PydanticObjectId, to_id: PydanticObjectId):
        try:
            role_assigned_match = db.role_assigned.find_one(
                {'toId': ObjectId(to_id), 'roleId': ObjectId(role_id)})

            if role_assigned_match:
                db.role_assigned.delete_one(
                    {'toId': ObjectId(to_id), 'roleId': ObjectId(role_id)})
        except Exception as e:
            raise e

    def has_permission(self, to_id: PydanticObjectId, organization_id: PydanticObjectId, role_id: PydanticObjectId, required_permission: str) -> bool:
        is_match = False
        try:
            role_assigned_match = db.role_assigned.find_one({'toId': ObjectId(
                to_id), 'organizationId': ObjectId(organization_id), 'roleId': ObjectId(role_id)})

            if role_assigned_match:
                role = db.role_collection.find_one({'_id': ObjectId(role_id)})
                for permission in role['permissions']:
                    if permission == required_permission:
                        is_match = True
        except Exception as e:
            raise e
        finally:
            return is_match

    def get_permissions(self, role_id: PydanticObjectId) -> List[str]:
        permissions = []
        try:
            role = db.role_collection.find_one({'_id': ObjectId(role_id)})
            for permission in role['permissions']:
                permissions.append(permission)
            return permissions
        except Exception as e:
            raise e

    def delete(self, organization_id: PydanticObjectId, role_id: PydanticObjectId):
        try:
            role = db.role_collection.find_one(
                {'_id': ObjectId(role_id), 'organizationId': ObjectId(organization_id)})
            if role:
                db.role_assigned.delete_many({'roleId': ObjectId(role_id)})
                db.role_collection.delete_one({'_id': ObjectId(role_id)})
        except Exception as e:
            raise e
