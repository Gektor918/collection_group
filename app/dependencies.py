import logging
from typing import Type, TypeVar

from auth import User
from auth import get_current_user as get_user
from db.session import get_session
from fastapi import Depends, Form, HTTPException, status
from pydantic import BaseModel, ValidationError
from services.router_service import RouterService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


T = TypeVar('T', bound=BaseModel)

async def get_router_service(
    db_session: AsyncSession = Depends(get_session),
) -> RouterService:
    return RouterService(db_session)

def get_verified_payload_access_dependency(
    model_class: Type[T],
    type_point: str,
    description: str = "",
    ):
    async def dependency(
        data: str = Form(..., description=description),
        user: User = Depends(get_user),
        router_service: RouterService = Depends(get_router_service),
    ) -> T:
        try:
            payload = model_class.model_validate_json(data)
        except ValidationError as e:
            logger.info("Invalid payload for %s: %s", model_class.__name__, e.errors())
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid payload",
            )
        await _check_company_access(user, type_point, payload.company_id, router_service)
        return payload
        
    return dependency

def get_company_access_dependency(type_point: str):
    async def dependency(
        company_id: int,
        user: User  = Depends(get_user),
        router_service: RouterService = Depends(get_router_service),
    ) :
        await _check_company_access(user, type_point, company_id, router_service)
        return user
        
    return dependency

async def _check_company_access(user, type_point, company_id, router_service):
    pass

