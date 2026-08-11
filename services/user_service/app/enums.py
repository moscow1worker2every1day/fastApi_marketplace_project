import enum


class UserRoles(enum.Enum):
    admin = "admin"
    user = "user"
    seller = "seller"

class TokenType(enum.Enum):
    TOKEN_TYPE_FIELD = "type"
    ACCESS_TOKEN_TYPE = "access"
    REFRESH_TOKEN_TYPE = "refresh"
