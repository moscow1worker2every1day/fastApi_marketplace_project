from enum import Enum


class DeleteProductMode(str, Enum):
    DELETE = "delete"
    SOFT = "soft"

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"Delete mode: {self.value}. Available: {self.__dict__}"