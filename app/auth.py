from dataclasses import dataclass
from fastapi import Header


@dataclass(frozen=True)
class User:
    id: int
    company_id: int
    is_platform_admin: bool = False


async def get_current_user(
    x_company_id: int = Header(1, description="Мок авторизации: компания пользователя"),
    x_platform_admin: bool = Header(False, description="Мок роли админа"),
) -> User:
    return User(id=1, company_id=x_company_id, is_platform_admin=x_platform_admin)
