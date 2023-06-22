from bson import ObjectId


class ApiKey:
    id: ObjectId
    name: str
    key: str
    user_id: ObjectId

    def __init__(self, name: str, key: str, user_id: ObjectId):
        self.name = name
        self.key = key
        self.user_id = user_id

