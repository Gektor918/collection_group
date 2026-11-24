

T = TypeVar('T', bound=BaseModel)

def get_verified_payload_access_dependency(
    model_class: Type[T],
    type_point: str,
    description: str = "",
    ):
    async def dependency(
        data: str = Form(..., description=description),
        user: BaseUser | AdminUser = Depends(get_user),
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
        user: BaseUser | AdminUser = Depends(get_user),
        router_service: RouterService = Depends(get_router_service),
    ) -> BaseUser | AdminUser:
        await _check_company_access(user, type_point, company_id, router_service)
        return user
        
    return dependency

async def _check_company_access(user, type_point, company_id, router_service):
    access_company = router_service.access_company_repository()
    access_user = router_service.access_repository()
    await access_company.access_company(user, company_id)
    await access_user.access_user(user, type_point, company_id)