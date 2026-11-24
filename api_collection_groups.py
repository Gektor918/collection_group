from fastapi import APIRouter, Depends, UploadFile

from db.dependencies import (get_company_access_dependency, get_router_service,
                             get_verified_payload_access_dependency)
from db.models.user import AdminUser, BaseUser
from schemas.description_api import ApiExampleCollectionGroup
from services.collection_group.schemas import (
    CollectionGroupCreateRequest, CollectionGroupUpdateListCommon,
    CollectionGroupUpdateOrderRequest, CollectionGroupUpdateRequest,
    CollItemId, CollItems, CollList, CollOrders, CollUpdateList)
from services.collection_group.utils.common import delete_file_by_url
from services.router_service import RouterService
from settings import TYPE_POINT_CMS

router = APIRouter(prefix="/tour", tags=["collection_groups"])


@router.get("/collection_group/all", response_model=CollList)
async def get_collection_groups(
    company_id: int,
    user: BaseUser | AdminUser = Depends(get_company_access_dependency(TYPE_POINT_CMS)),
    router_service: RouterService = Depends(get_router_service),
):
    cgs = router_service.collection_group_service()
    return CollList(items=await cgs.list_groups(company_id))

@router.post("/collection_group/create", response_model=CollItems)
async def create_collection_group(
    image: UploadFile | None = None,
    payload: CollectionGroupCreateRequest = Depends(get_verified_payload_access_dependency(
        CollectionGroupCreateRequest,
        TYPE_POINT_CMS,
        ApiExampleCollectionGroup.create_group
    )),
    router_service: RouterService = Depends(get_router_service),
):
    storage_manager = router_service.storage_manager_repository()
    image_url: str | None = None
    if image:
        image_url = await storage_manager.process_upload_file(
            await storage_manager.copy_upload_file(image),
            collection_group=True,
        )

    cgs = router_service.collection_group_service()
    try:
        return CollItems(items=await cgs.create_group(
            company_id=payload.company_id,
            lang=payload.lang,
            image=image_url,
        ))
    except Exception:
        await delete_file_by_url(storage_manager, image_url)
        raise

@router.put("/collection_group/order", response_model=CollOrders)
async def update_collection_group_order(
    payload: CollectionGroupUpdateOrderRequest = Depends(get_verified_payload_access_dependency(
        CollectionGroupUpdateOrderRequest,
        TYPE_POINT_CMS,
        ApiExampleCollectionGroup.update_order
    )),
    router_service: RouterService = Depends(get_router_service),
):
    cgs = router_service.collection_group_service()
    return CollOrders(items=await cgs.update_order(
        company_id=payload.company_id,
        orders=payload.orders,
    ))

@router.put("/collection_group/update", response_model=CollItems)
async def update_collection_group(
    image: UploadFile | None = None,
    payload: CollectionGroupUpdateRequest = Depends(get_verified_payload_access_dependency(
        CollectionGroupUpdateRequest,
        TYPE_POINT_CMS,
        ApiExampleCollectionGroup.update_group
    )),
    router_service: RouterService = Depends(get_router_service),
):
    storage_manager = router_service.storage_manager_repository()

    image_url: str | None = None
    if image:
        image_url = await storage_manager.process_upload_file(
            await storage_manager.copy_upload_file(image),
            collection_group=True,
        )

    cgs = router_service.collection_group_service()
    try:
        outcome = await cgs.update_group(
            group_id=payload.id,
            company_id=payload.company_id,
            lang=payload.lang,
            image=image_url,
            disable=payload.disable,
        )
    except Exception:
        await delete_file_by_url(storage_manager, image_url)
        raise

    if image_url and outcome.old_image != image_url:
        await delete_file_by_url(storage_manager, outcome.old_image)

    return CollItems(items=outcome.dto)

@router.put("/collection_group/update_list", response_model=CollUpdateList)
async def update_collection_group_list(
    payload: CollectionGroupUpdateListCommon = Depends(get_verified_payload_access_dependency(
        CollectionGroupUpdateListCommon,
        TYPE_POINT_CMS,
        ApiExampleCollectionGroup.update_group_list
    )),
    router_service: RouterService = Depends(get_router_service),
):
    cgs = router_service.collection_group_service()
    return CollUpdateList(**await cgs.update_group_list(
        group_id=payload.id,
        company_id=payload.company_id,
        new_collections=payload.new_collections,
        delete_collections=payload.delete_collections,
    ))

@router.delete("/collection_group/delete", response_model=CollItemId)
async def delete_collection_group(
    group_id: int,
    company_id: int,
    router_service: RouterService = Depends(get_router_service),
    user: BaseUser | AdminUser = Depends(get_company_access_dependency(TYPE_POINT_CMS)),
):
    storage_manager = router_service.storage_manager_repository()
    cgs = router_service.collection_group_service()
    result = await cgs.delete_group(group_id, company_id)
    await delete_file_by_url(storage_manager, result.old_image)
    return CollItemId(items=result.group_id)
