from dataclasses import dataclass


@dataclass(slots=True)
class BaseUser:
    id: int
    company_id: int | None = None
    type_point: str | None = None


@dataclass(slots=True)
class AdminUser(BaseUser):
    is_superuser: bool = True
