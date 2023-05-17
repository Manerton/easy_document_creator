from bson import ObjectId


class Process:
    id: ObjectId
    name: str
    description: str
    file_type: str
    file_id: ObjectId
    user_id: ObjectId

    def __init__(self, name: str, description: str, file_type: str, file_id: ObjectId, user_id: ObjectId):
        self.name = name
        self.description = description
        self.file_type = file_type
        self.file_id = file_id
        self.user_id = user_id
