from pymongo.errors import DuplicateKeyError as MongoDBDuplicateKeyError
from quest_maker_api_shared_library.custom_types import PydanticObjectId
from quest_maker_api_shared_library.errors.database import DuplicateKeyError

from core.config.env import Env

env = Env()


class Permissions:
    read_own = 'read:own'
    write_own = 'write:own'
    delete_own = 'delete:own'
    read_org = 'read:org'
    write_org = 'write:org'
    delete_org = 'delete:org'
    read_all = 'read:all'
    write_all = 'write:all'
    delete_all = 'delete:all'
    administer = 'administer'
    access_control = 'access control'

    @classmethod
    def __iter__(cls):
        return iter([
            cls.read_own,
            cls.write_own,
            cls.delete_own,
            cls.read_org,
            cls.write_org,
            cls.delete_org,
            cls.read_all,
            cls.write_all,
            cls.delete_all,
            cls.administer,
            cls.access_control
        ])
