from typing import Type, TypeVar, Generic
from pydantic import ValidationError, BaseModel
from src.repositories import NodeRepository, EdgeRepository
from src.types import OperationEnum
from src.models.pydantic_models import (
    NodeModel,
    HasRecordCreate,
    HasRecordRead,
    HasRecordUpdate,
    HasActiveRecordRead,
    HasActiveRecordCreate,
    HasActiveRecordUpdate,
    HasPreviousRecordCreate,
    HasPreviousRecordRead,
    HasPreviousRecordUpdate,
)
from src.models.neomodel_entities import (
    RecorderEdge,
    RecordedNode,
    NodeRecord,
    HasRecord,
    HasActiveRecord,
    HasPreviousRecord,
)

from src.services import NodeRecordService

TNodeRepo = TypeVar("TNodeRepo", bound=NodeRepository)
TCreate = TypeVar("TCreate", bound=BaseModel)  # Pydantic create class
TRead = TypeVar("TRead", bound=NodeModel)  # Pydantic read class
TUpdate = TypeVar("TUpdate", bound=BaseModel)

TEntity = TypeVar("TEntity", bound=RecordedNode)
TRecord = TypeVar("TRecord", bound=NodeRecord)
TRelationship = TypeVar("TRelationship", bound=RecorderEdge)


class RecordedNodeService(Generic[TEntity, TRecord, TRead]):
    def __init__(
        self,
        repository: TNodeRepo,
        record_service: NodeRecordService,
        create_model: Type[TCreate],
    ) -> None:
        self.repository = repository
        self.record_service = record_service
        self.create_model = create_model

        self.has_record_repo = EdgeRepository[
            HasRecord,
            TEntity,
            TRecord,
            HasRecordCreate,
            HasRecordRead,
            HasRecordUpdate,  # TODO: HasRecordUpdate is unused
        ](
            rel_model=HasRecord,
            start_node_model=self.repository.node_model,
            end_node_model=self.record_service.repository.node_model,
            create_model=HasRecordCreate,
            read_model=HasRecordRead,
        )

        self.has_active_record_repo = EdgeRepository[
            HasActiveRecord,
            TEntity,
            TRecord,
            HasActiveRecordCreate,
            HasActiveRecordRead,
            HasActiveRecordUpdate,
        ](
            rel_model=HasActiveRecord,
            start_node_model=self.repository.node_model,
            end_node_model=self.record_service.repository.node_model,
            create_model=HasActiveRecordCreate,
            read_model=HasActiveRecordRead,
        )

        self.has_previous_record_repo = EdgeRepository[
            HasPreviousRecord,
            TRecord,
            TRecord,
            HasPreviousRecordCreate,
            HasPreviousRecordRead,
            HasPreviousRecordUpdate,
        ](
            rel_model=HasPreviousRecord,
            start_node_model=self.record_service.repository.node_model,
            end_node_model=self.record_service.repository.node_model,
            create_model=HasPreviousRecordCreate,
            read_model=HasPreviousRecordRead,
        )

    def create_node(self, data: dict) -> TRead:
        # Validierung und Konvertierung der Eingabedaten in ein Pydantic-Objekt
        try:
            validated_data = self.create_model.model_validate(data)
        except ValidationError as e:
            raise ValueError("Validation error while creating entity") from e

        return self.repository.create(validated_data)

    def create(self, data: dict) -> TRead:
        # Create recorded node
        read_node = self.create_node(data)

        # Create node record
        record_data = data | {"operation": OperationEnum.CREATED}
        read_record = self.record_service.create(record_data)

        # Connect recorded node by has record edge to node record
        has_record_create = HasRecordCreate(
            start_uuid=read_node.uuid, end_uuid=read_record.uuid
        )
        self.has_record_repo.create("records", has_record_create)

        # Connect recorded node by has active record edge to node record
        has_active_record_create = HasActiveRecordCreate(
            start_uuid=read_node.uuid, end_uuid=read_record.uuid
        )
        self.has_active_record_repo.create("active_record", has_active_record_create)

        # Return the recorded node
        return read_node

    def read(self, uuid: str) -> TRead:
        return self.repository.read(uuid)

    def update(self, uuid: str, data: dict) -> TRead | False:
        read_node = self.repository.read(uuid)
        if read_node:

            # Get has active record edge
            read_has_active_record = self.has_active_record_repo.read(
                relationship="active_record",
                uuid=read_node.uuid,
            )

            # Get old data from active record node
            read_active_record = self.record_service.read(
                uuid=read_has_active_record.end_uuid
            )
            old_data = read_active_record.dict()
            del old_data["uuid"]
            del old_data["created_at"]

            # Create node record
            record_data = old_data | data | {"operation": OperationEnum.UPDATED}
            read_record = self.record_service.create(record_data)

            # Connect recorded node by has record edge to node record
            rel_data = HasRecordCreate(
                start_uuid=read_node.uuid, end_uuid=read_record.uuid
            )
            self.has_record_repo.create("records", rel_data)

            # Connect recorded node by has active record edge to node record
            has_active_record_update = HasActiveRecordUpdate(
                start_uuid=read_node.uuid, end_uuid=read_record.uuid
            )
            read_has_active_record = self.has_active_record_repo.update(
                "active_record", has_active_record_update
            )

            has_previous_record_create = HasPreviousRecordCreate(
                start_uuid=read_active_record.uuid,
                end_uuid=read_has_active_record.end_uuid,
            )
            self.has_previous_record_repo.create("previous", has_previous_record_create)

            return read_node
        return False

    def delete(self, uuid: str) -> TRead | False:
        read_node = self.repository.read(uuid)
        if read_node:

            # Get has active record edge
            read_has_active_record = self.has_active_record_repo.read(
                relationship="active_record",
                uuid=read_node.uuid,
            )

            # Get old data from active record node
            read_active_record = self.record_service.read(
                uuid=read_has_active_record.end_uuid
            )
            old_data = read_active_record.dict()
            del old_data["uuid"]
            del old_data["created_at"]

            # Create node record
            record_data = old_data | {"operation": OperationEnum.DELETED}
            read_record = self.record_service.create(record_data)

            # Connect recorded node by has record edge to node record
            rel_data = HasRecordCreate(
                start_uuid=read_node.uuid, end_uuid=read_record.uuid
            )
            self.has_record_repo.create("records", rel_data)

            # Connect recorded node by has active record edge to node record
            has_active_record_update = HasActiveRecordUpdate(
                start_uuid=read_node.uuid, end_uuid=read_record.uuid
            )
            read_has_active_record = self.has_active_record_repo.update(
                "active_record", has_active_record_update
            )

            has_previous_record_create = HasPreviousRecordCreate(
                start_uuid=read_active_record.uuid,
                end_uuid=read_has_active_record.end_uuid,
            )
            self.has_previous_record_repo.create("previous", has_previous_record_create)

        return False
