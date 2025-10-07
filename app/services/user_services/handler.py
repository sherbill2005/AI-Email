from app.db_utils.mongo import db
from app.models.user_model import User


class UserService():
    def __init__(self,):
        self.collection = db.users

    async def get_user_by_email(self, email: str) -> User | None:
        user_data = self.collection.find_one({"email": email})
        if user_data:
            return User(**user_data)
        return None

    async def create_user(self, email: str, name: str) -> User | None:
        new_user_data = User(email=email, name=name).to_dict()
        result = self.collection.insert_one(new_user_data)
        created_user_doc = self.collection.find_one({"_id": result.inserted_id})
        if created_user_doc:
            return User(**created_user_doc)
        return None