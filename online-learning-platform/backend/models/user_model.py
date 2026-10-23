from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import get_db
from backend.models.utils import serialize_doc, to_object_id

def get_users_collection():
    return get_db()["users"]


class UserModel:
    @staticmethod
    def create_user(name, email, password, role="student", bio="", avatar=""):
        collection = get_users_collection()
        email_clean = email.strip().lower()

        if collection.find_one({"email": email_clean}):
            return None, "User with this email already exists"

        if not avatar:
            # Generate attractive modern avatar placeholder
            avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={name.replace(' ', '+')}&backgroundColor=2563eb,7c3aed,0ea5e9"

        now = datetime.now(timezone.utc)
        user_doc = {
            "name": name.strip(),
            "email": email_clean,
            "password_hash": generate_password_hash(password),
            "role": role if role in ("admin", "student") else "student",
            "bio": bio.strip(),
            "avatar": avatar,
            "created_at": now,
            "updated_at": now
        }

        result = collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return UserModel.sanitize(user_doc), None

    @staticmethod
    def find_by_email(email):
        collection = get_users_collection()
        return collection.find_one({"email": email.strip().lower()})

    @staticmethod
    def find_by_id(user_id):
        collection = get_users_collection()
        oid = to_object_id(user_id)
        if not oid:
            return None
        return collection.find_one({"_id": oid})

    @staticmethod
    def verify_password(stored_hash, candidate_password):
        if not stored_hash or not candidate_password:
            return False
        return check_password_hash(stored_hash, candidate_password)

    @staticmethod
    def update_profile(user_id, name=None, bio=None, avatar=None):
        collection = get_users_collection()
        oid = to_object_id(user_id)
        if not oid:
            return None, "Invalid user ID"

        update_fields = {"updated_at": datetime.now(timezone.utc)}
        if name is not None:
            update_fields["name"] = name.strip()
        if bio is not None:
            update_fields["bio"] = bio.strip()
        if avatar is not None:
            update_fields["avatar"] = avatar.strip()

        collection.update_one({"_id": oid}, {"$set": update_fields})
        updated = collection.find_one({"_id": oid})
        return UserModel.sanitize(updated), None

    @staticmethod
    def sanitize(user_doc):
        if not user_doc:
            return None
        serialized = serialize_doc(user_doc)
        serialized.pop("password_hash", None)
        return serialized

    @staticmethod
    def get_all_users(role=None):
        collection = get_users_collection()
        query = {}
        if role:
            query["role"] = role
        users = list(collection.find(query).sort("created_at", -1))
        return [UserModel.sanitize(u) for u in users]

    @staticmethod
    def delete_user(user_id):
        collection = get_users_collection()
        oid = to_object_id(user_id)
        if not oid:
            return False
        res = collection.delete_one({"_id": oid})
        return res.deleted_count > 0
