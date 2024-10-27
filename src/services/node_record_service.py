from typing import Type, TypeVar, Generic
from pydantic import ValidationError, BaseModel
from src.repositories import NodeRepository
from src.models.pydantic_models import (
    NodeModel,
)
from src.models.neomodel_entities import (
    RecorderEdge,
    RecordedNode,
    NodeRecord,
)

TNodeRepo = TypeVar("TNodeRepo", bound=NodeRepository)
TCreate = TypeVar("TCreate", bound=BaseModel)  # Pydantic create class
TRead = TypeVar("TRead", bound=NodeModel)  # Pydantic read class
TUpdate = TypeVar("TUpdate", bound=BaseModel)

TEntity = TypeVar("TEntity", bound=RecordedNode)
TRecord = TypeVar("TRecord", bound=NodeRecord)
TRelationship = TypeVar("TRelationship", bound=RecorderEdge)


class NodeRecordService(Generic[TRead]):
    def __init__(
        self,
        repository: TNodeRepo,
        create_model: Type[TCreate],
    ) -> None:
        self.repository = repository
        self.create_model = create_model

    def create(self, data: dict) -> TRead:
        # Validierung und Konvertierung der Eingabedaten in ein Pydantic-Objekt

        try:
            validated_data = self.create_model.model_validate(data)
        except ValidationError as e:
            raise ValueError("Validation error while creating entity") from e

        return self.repository.create(validated_data)

    def read(self, uuid: str) -> TRead:
        return self.repository.read(uuid)
