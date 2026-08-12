import enum


class UserRoles(enum.Enum):
    admin = "admin"
    user = "user"
    seller = "seller"

class TokenType(enum.Enum):
    TOKEN_TYPE_FIELD = "type"
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"


class SortOrder(enum.Enum):
    asc = "asc"
    desc = "desc"


class UserSortField(enum.Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    first_name = "first_name"
    last_name = "last_name"
    email = "email"
    id = "id"
