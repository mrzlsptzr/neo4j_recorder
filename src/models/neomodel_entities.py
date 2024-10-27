from neomodel import (
    StructuredNode,
    StructuredRel,
    StringProperty,
    DateTimeProperty,
    RelationshipTo,
    RelationshipFrom,
)
from uuid import uuid4


class RecorderEdge(StructuredRel):
    uuid = StringProperty(unique_index=True, default=uuid4)
    created_at = DateTimeProperty(default_now=True)


class HasRecord(RecorderEdge): ...


class HasActiveRecord(RecorderEdge): ...


class HasPreviousRecord(RecorderEdge): ...


class RecorderNode(StructuredNode):
    __abstract_node__ = True

    uuid = StringProperty(unique_index=True, default=uuid4)
    created_at = DateTimeProperty(default_now=True)


class NodeRecord(RecorderNode):
    operation = StringProperty(required=True)
    previous = RelationshipFrom(
        "NodeRecord", "HAS_PREVIOUS_RECORD", model=HasPreviousRecord
    )


class RecordedNode(RecorderNode):
    records = RelationshipTo(NodeRecord, "HAS_RECORD", model=HasRecord)
    active_record = RelationshipTo(
        NodeRecord, "HAS_ACTIVE_RECORD", model=HasActiveRecord
    )
