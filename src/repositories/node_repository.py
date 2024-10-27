from src.models.neomodel_entities import RecorderEdge, RecorderNode
from pydantic import BaseModel
from src.models.pydantic_models import NodeModel, EdgeModel
from typing import Type, TypeVar, Generic, Optional

TNodeCreate = TypeVar("TNodeCreate", bound=BaseModel)  # Pydantic create class
TNodeRead = TypeVar("TNodeRead", bound=NodeModel)  # Pydantic read class
TNode = TypeVar("TNode", bound=RecorderNode)  # Neomodel node class


class NodeRepository(Generic[TNodeCreate, TNodeRead, TNode]):
    def __init__(self, node_model: Type[TNode], read_model: Type[TNodeRead]):
        self.node_model = node_model  # Neomodel node class
        self.read_model = read_model  # Pydantic read class

    def create(self, data: TNodeCreate) -> TNodeRead:
        # Create and save a neomodel object from the pydantic create data in the database
        node_instance = self.node_model(**data.model_dump())
        node_instance.save()

        # Validate the data against the pydantic read model
        return self.read_model.model_validate(node_instance.__properties__)

    def read(self, uuid: str) -> TNodeRead:
        node_instance = self.node_model.nodes.get_or_none(uuid=uuid)

        if node_instance is None:
            raise ValueError(f"Node with uuid {uuid} not found")

        # Validate the data against the pydantic read model
        return self.read_model.model_validate(node_instance)
