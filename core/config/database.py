from pymongo.mongo_client import MongoClient

from core.config.env import Env

env = Env()


class OrganizationDatabase:
    uri = 'mongodb+srv://' + env.MONGODB_USERNAME + ':' + \
        env.MONGODB_PASSWORD.get_secret_value() + \
        '@' + env.MONGODB_CLUSTER + '/?retryWrites=true&w=majority'
    client = MongoClient(uri)
    # Set the database name to 'organization_db'
    db = client['organization_db']

    # Set the collection name to 'organization'
    organization_collection = db['organization']

    # Set the collection name to 'organization_member'
    organization_member_collection = db['organization_member']
