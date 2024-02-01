from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from quest_maker_api_shared_library.token_manager import TokenManager
from quest_maker_api_shared_library.custom_types import PydanticObjectId
from quest_maker_api_shared_library.errors.authentication import InvalidTokenError, ExpiredTokenError
import requests

from core.config.env import Env
from core.errors.database import DocumentNotFoundError
from core.models.organization import OrganizationCreate
from core.services.organization import OrganizationService


organization = APIRouter()
bearer = HTTPBearer()
service = OrganizationService()
env = Env()
token_manager = TokenManager(key=env.JWT_SECRET_KEY.get_secret_value(),
                             jwt_expiration_time_in_minutes=env.JWT_EXPIRATION_TIME_IN_MINUTES,)


@organization.post('/')
# Create new organization instance
def create_organization(data: OrganizationCreate, token: HTTPAuthorizationCredentials = Security(bearer)):
    try:
        payload = token_manager.decode_token(token=token.credentials)
        owner_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                id = service.create(owner_id=owner_id, data=data)
                try:
                    # Set up request headers
                    headers = {'Authorization': f'Bearer {token.credentials}'}

                    json_data = {}
                    json_data['organizations'] = []

                    # Pass organization details to Authentication service
                    organizations = service.read_all(member_id=owner_id)
                    for organization in organizations:
                        for organization in organizations:
                            organization.id = str(organization.id)
                            organization.ownerId = str(organization.ownerId)
                            organization.memberId = str(organization.memberId)
                        json_data['organizations'].append(
                            organization.model_dump())

                    response = requests.put(url=f'{env.AUTHENTICATION_SERVICE_URL}auth/',
                                            json=json_data,
                                            headers=headers)

                    if response.status_code == HTTPStatus.OK:
                        return id

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
        owner_id = str(payload['sub'])
        scope = str(payload['scope'])
        if 'access_token' in scope.split():
            try:
                organization = service.read(
                    owner_id=owner_id, organization_id=organization_id)
                return organization

            except DocumentNotFoundError:
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={
                                    'message': 'Resource not found'})
            except HTTPException:
                raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail={
                                    'message': 'Invalid request'})
    except HTTPException:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={
            'message': 'Unauthorized access or Insufficient scope'})


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
    except HTTPException:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail={
            'message': 'Unauthorized access or Insufficient scope'})


@organization.put('/')
# Update organization instance
def update_organization(token: HTTPAuthorizationCredentials = Security(bearer)):
    pass


@organization.delete('/')
# Delete organization instance
def delete_organization(token: HTTPAuthorizationCredentials = Security(bearer)):
    pass
