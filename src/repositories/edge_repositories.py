from src.models.neomodel_entities import RecorderEdge, RecorderNode
from pydantic import BaseModel
from src.models.pydantic_models import EdgeModel
from typing import Type, TypeVar, Generic, Optional


TRelationship = TypeVar("TRelationship", bound=RecorderEdge)
TStartNode = TypeVar("TStartNode", bound=RecorderNode)
TEndNode = TypeVar("TEndNode", bound=RecorderNode)
TCreate = TypeVar("TCreate", bound=BaseModel)
TRead = TypeVar("TRead", bound=EdgeModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class EdgeRepository(
    Generic[TRelationship, TStartNode, TEndNode, TCreate, TRead, TUpdate]
):
    def __init__(
        self,
        rel_model: Type[TRelationship],
        start_node_model: Type[TStartNode],
        end_node_model: Type[TEndNode],
        create_model: Type[TCreate],
        read_model: Type[TRead],
    ):
        self.rel_model = rel_model
        self.start_node_model = start_node_model
        self.end_node_model = end_node_model
        self.create_model = create_model
        self.read_model = read_model

    def create(self, relationship: str, data: TCreate) -> Optional[TRead]:
        """

        Creates a new relationship based on the uuid of the nodes.

        Args:
            data:

        Returns:

        """

        # Get start node and end node from the neomodel models by their uuid
        start_node = self.start_node_model.nodes.get_or_none(uuid=data.start_uuid)
        end_node = self.end_node_model.nodes.get_or_none(uuid=data.end_uuid)

        if start_node is None or end_node is None:
            return None

        # Validieren und Daten in Beziehungsklasse umwandeln
        rel_instance = self.rel_model(**data.model_dump(exclude_unset=True))

        # Verbinde die Knoten
        getattr(start_node, relationship).connect(
            end_node, data.model_dump(exclude={"start_uuid", "end_uuid"})
        )

        # Rückgabe des Pydantic-Read-Modells
        return self.read_model.from_orm(rel_instance)

    def read(
        self,
        relationship: str,
        uuid: str,
    ) -> Optional[TRead]:
        start_node = self.start_node_model.nodes.get_or_none(uuid=uuid)
        end_node = getattr(start_node, relationship).single()
        rel = getattr(start_node, relationship).relationship(end_node)

        if start_node:
            return self.read_model(
                uuid=rel.uuid,
                created_at=rel.created_at,
                start_uuid=start_node.uuid,
                end_uuid=end_node.uuid,
            )
        return None

    def update(self, relationship: str, data: TUpdate) -> Optional[TRead]:
        """

        Creates a new relationship based on the uuid of the nodes.

        Args:
            data:

        Returns:

        """

        # Get start node and end node from the neomodel models by their uuid
        start_node = self.start_node_model.nodes.get_or_none(uuid=data.start_uuid)
        end_node = self.end_node_model.nodes.get_or_none(uuid=data.end_uuid)

        if start_node is None or end_node is None:
            return None

        # Validieren und Daten in Beziehungsklasse umwandeln
        rel_instance = self.rel_model(**data.model_dump(exclude_unset=True))

        var = data.model_dump(exclude={"start_uuid", "end_uuid"})

        # Verbinde die Knoten
        getattr(start_node, relationship).replace(
            end_node,
            data.model_dump(exclude={"start_uuid", "end_uuid"}),
        )

        # Rückgabe des Pydantic-Read-Modells
        return self.read_model.from_orm(rel_instance)

    def get_relationship(
        self, start_node_uuid: str, end_node_uuid: str
    ) -> Optional[TRead]:
        """Holt die Beziehung zwischen zwei Knoten basierend auf deren UUIDs."""
        start_node = self.start_node_model.nodes.get_or_none(uuid=start_node_uuid)
        end_node = self.end_node_model.nodes.get_or_none(uuid=end_node_uuid)

        if start_node is None or end_node is None:
            return None

        rel_instance = start_node.relationship.relationship(end_node, self.rel_model)
        if rel_instance is None:
            return None

        # Rückgabe als Pydantic-Read-Modell
        return self.read_model.from_orm(rel_instance)

    def delete_relationship(self, start_node_uuid: str, end_node_uuid: str) -> bool:
        """Löscht die Beziehung zwischen zwei Knoten basierend auf deren UUIDs."""
        start_node = self.start_node_model.nodes.get_or_none(uuid=start_node_uuid)
        end_node = self.end_node_model.nodes.get_or_none(uuid=end_node_uuid)

        if start_node:
            rel_instance = start_node.relationship.relationship(
                end_node, self.rel_model
            )
            if rel_instance:
                rel_instance.delete()
                return True
        return False
