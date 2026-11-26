from repository import CollectionGroupRepository
from service import CollectionGroupService
from services.storage import StorageService
from sqlalchemy.ext.asyncio import AsyncSession


class RouterService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.collection_group_repo = CollectionGroupRepository(db_session)
        self.storage_service = StorageService()

    def collection_group_service(self) -> CollectionGroupService:
        return CollectionGroupService(
            repo=self.collection_group_repo, 
            session=self.db_session
        )

    def storage_manager_repository(self) -> StorageService:
        return self.storage_service
