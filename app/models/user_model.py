from bson import objectid

class User:
    def __init__(self, email: str, name : str=None, last_processed_history_id: str | None = None, _id=None):
        print(f"[User Model __init__] Received: email={email}, name={name}, last_processed_history_id={last_processed_history_id}, _id={_id}")
        self.email = email
        self.name = name
        self.last_processed_history_id = last_processed_history_id
        self._id = _id

    def to_dict(self):
        return {
            "email": self.email,
            "name": self.name,
            "last_processed_history_id": self.last_processed_history_id
        }