from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from quest_maker_api_shared_library.token_manager import TokenManager
from quest_maker_api_shared_library.custom_types import PydanticObjectId
from quest_maker_api_shared_library.errors.authentication import InvalidTokenError, ExpiredTokenError
import requests

from core.config.env import Env
from core.errors.database import DocumentNotFoundError
from core.models.organization import OrganizationCreate, OrganizationUpdate
from core.models.roles import RoleAssignedInDB
from core.services.organization import OrganizationService
from core.utils.managers.roles import RoleManager


organization = APIRouter()
bearer = HTTPBearer()
service = OrganizationService()
env = Env()
token_manager = TokenManager(key=env.JWT_SECRET_KEY.get_secret_value(),
                             jwt_expiration_time_in_minutes=env.JWT_EXPIRATION_TIME_IN_MINUTES,)
role_manager = RoleManager()


@organization.post('/')
# Create new organization instance
def create_organization(data: OrganizationCreate, token: HTTPAuthorizationCredentials = Security(bearer)):
    try:
        payload = token_manager.decode_token(token=token.credentials)
        owner_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                organization_id = service.create(owner_id=owner_id, data=data)
                role_ids = role_manager.setup(organization_id=organization_id)
                if role_ids:
                    role_manager.assign_role(data=RoleAssignedInDB(
                        toId=owner_id, organizationId=organization_id, roleId=role_ids[0]))
                try:
                    # Set up request headers
                    headers = {'Authorization': f'Bearer {token.credentials}'}

                    json_data = {}
                    json_data['organizations'] = []
                    json_data['roles'] = []

                    # Pass organization details to Authentication service
                    organizations = service.read_all(member_id=owner_id)
                    for organization in organizations:
                        organization.id = str(organization.id)
                        organization.ownerId = str(organization.ownerId)
                        json_data['organizations'].append(
                            organization.model_dump())

                    # Pass role details to Authentication service
                    roles = role_manager.get_roles(to_id=owner_id)
                    for role in roles:
                        role['_id'] = str(role['_id'])
                        role['organizationId'] = str(role['organizationId'])
                        json_data['roles'].append(role)

                    response = requests.put(url=f'{env.AUTHENTICATION_SERVICE_URL}auth/',
                                            json=json_data,
                                            headers=headers)

                    if response.status_code == HTTPStatus.OK:
                        return str(organization_id)

                except HTTPException:
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail={
                                        'message': 'Internal Server Error'})

            except HTTPException:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail={'message': 'Invalid request'})
        else:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={
                                'message': 'Unauthorized access or Insufficient scope'})
    except ExpiredTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})
    except InvalidTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})


@organization.get('/')
# Fetch organization instance
def read_organization(organization_id: PydanticObjectId, token: HTTPAuthorizationCredentials = Security(bearer)):
    try:
        payload = token_manager.decode_token(token=token.credentials)
        member_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                organization = service.read(
                    member_id=member_id, organization_id=organization_id)
                return organization

            except DocumentNotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={
                                    'message': 'Resource not found'})
            except HTTPException:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail={
                                    'message': 'Invalid request'})
        else:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={
                'message': 'Unauthorized access or Insufficient scope'})
    except ExpiredTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})
    except InvalidTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})


@organization.get('/all/')
# Fetch all organization instances associated with an authenticated user
def read_organizations(token: HTTPAuthorizationCredentials = Security(bearer)):
    try:
        payload = token_manager.decode_token(token=token.credentials)
        member_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                organizations = service.read_all(member_id=member_id)
                return organizations

            except DocumentNotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={
                                    'message': 'Resource not found'})
            except HTTPException:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail={
                                    'message': 'Invalid request'})
    except ExpiredTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})
    except InvalidTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})


@organization.put('/{organization_id}')
# Update organization instance
def update_organization(organization_id: PydanticObjectId, data: OrganizationUpdate, token: HTTPAuthorizationCredentials = Security(bearer)):
    try:
        payload = token_manager.decode_token(token=token.credentials)
        owner_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                data = service.update(owner_id=owner_id, organization_id=str(
                    organization_id), data=data)
                try:
                    # Set up request headers
                    headers = {'Authorization': f'Bearer {token.credentials}'}

                    json_data = {}
                    json_data['organizations'] = []

                    # Pass organization details to Authentication service
                    organizations = service.read_all(member_id=owner_id)
                    for organization in organizations:
                        organization.id = str(organization.id)
                        organization.ownerId = str(organization.ownerId)
                        json_data['organizations'].append(
                            organization.model_dump())

                    response = requests.put(url=f'{env.AUTHENTICATION_SERVICE_URL}auth/',
                                            json=json_data,
                                            headers=headers)

                    if response.status_code == HTTPStatus.OK:
                        return data

                except HTTPException:
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail={
                                        'message': 'Internal Server Error'})

            except HTTPException:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST, detail={'message': 'Invalid request'})
        else:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={
                                'message': 'Unauthorized access or Insufficient scope'})
    except ExpiredTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})
    except InvalidTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})


@organization.delete('/{organization_id}')
# Delete organization instance
def delete_organization(organization_id: PydanticObjectId, token: HTTPAuthorizationCredentials = Security(bearer)):
    try:
        payload = token_manager.decode_token(token=token.credentials)
        owner_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                service.delete(owner_id=owner_id,
                               organization_id=str(organization_id))
                try:
                    # Set up request headers
                    headers = {'Authorization': f'Bearer {token.credentials}'}

                    json_data = {}
                    json_data['organizations'] = []

                    # Pass organization details to Authentication service
                    organizations = service.read_all(member_id=owner_id)
                    for organization in organizations:
                        organization.id = str(organization.id)
                        organization.ownerId = str(organization.ownerId)
                        json_data['organizations'].append(
                            organization.model_dump())

                    response = requests.put(url=f'{env.AUTHENTICATION_SERVICE_URL}auth/',
                                            json=json_data,
                                            headers=headers)

                    if response.status_code == HTTPStatus.OK:
                        return {"message": "Organization deleted successfully"}

                except HTTPException:
                    raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail={
                                        'message': 'Internal Server Error'})

            except DocumentNotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={
                                    'message': 'Organization not found'})
            except HTTPException:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail={
                                    'message': 'Invalid request'})
        else:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={
                                'message': 'Unauthorized access or Insufficient scope'})
    except ExpiredTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})
    except InvalidTokenError as e:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail={
                            'message': f'{e.detail}'})
