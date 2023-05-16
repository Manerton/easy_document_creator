import uuid

from flask_login import UserMixin
from pydantic import Field, EmailStr


class User(UserMixin):
    id: uuid = Field(...)
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    def __init__(self, name, email, password, id=None):
        self.name = name
        self.email = email
        self.password = password
        self.id = id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


