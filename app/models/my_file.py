from bson import ObjectId


class MyFile:
    filename: str
    file_id: ObjectId
    template_id: ObjectId

    def __init__(self, filename: str, file_id: ObjectId, template_id: ObjectId):
        self.filename = filename
        self.file_id = file_id
        self.template_id = template_id
