from datetime import datetime
from pydantic import BaseModel, create_model, Field
from pydantic.fields import FieldInfo
from src.types import OperationEnum
from typing import Dict
from uuid import UUID


class NodeModel(BaseModel):
    uuid: UUID  # = Field(..., description="A unique identifier.")
    created_at: datetime


class EntityCreateModel(BaseModel): ...


class EntityReadModel(NodeModel): ...


class EntityUpdateModel(BaseModel): ...


class EntityDeleteModel(BaseModel): ...


class RecordCreateModel(BaseModel):
    operation: OperationEnum = Field(..., description="Operation to be performed")

    class Config:
        use_enum_values = True


class RecordReadModel(NodeModel):
    operation: OperationEnum = Field(..., description="Operation to be performed")

    class Config:
        use_enum_values = True


def create_entity_create_model(model: NodeModel):
    """
    Create a generic model for create operations.

    Args:
        model: The model to create the create operation model from.

    Returns: A create operation model.

    """
    exclude_fields = {"uuid", "created_at"}
    fields = {
        **{
            name: (field.annotation, field)
            for name, field in EntityCreateModel.model_fields.items()
            if name not in exclude_fields
        },
        **{
            name: (field.annotation, field)
            for name, field in model.model_fields.items()
            if name not in exclude_fields
        },
    }

    # class Config:
    # arbitrary_types_allowed = True

    return create_model(f"{model.__name__}Create", **fields)


def create_entity_read_model(model: NodeModel):
    """
    Create a generic model for read operations.

    Args:
        model: The model to create the read operation model from.

    Returns: A read operation model.

    """
    fields: Dict[str, tuple] = {
        **{
            name: (
                field.annotation,
                FieldInfo.from_field(field, required=False),
            )
            for name, field in EntityReadModel.model_fields.items()
        },
    }

    class Config:
        # arbitrary_types_allowed = True
        from_attributes = True

    return create_model(f"{model.__name__}Read", **fields, __config__=Config)


def create_entity_update_model(model: NodeModel):
    """
    Create a generic model for create operations.

    Args:
        model: The model to create the create operation model from.

    Returns: A create operation model.

    """
    exclude_fields = {"uuid", "created_at"}
    fields = {
        **{
            name: (
                field.annotation,
                FieldInfo.from_field(field, required=False),
            )
            for name, field in EntityCreateModel.model_fields.items()
            if name not in exclude_fields
        },
        **{
            name: (field.annotation, field)
            for name, field in model.model_fields.items()
            if name not in exclude_fields
        },
    }

    # class Config:
    # arbitrary_types_allowed = True

    return create_model(f"{model.__name__}Update", **fields)


def create_record_create_model(model: NodeModel):
    """
    Create a generic model for create operations.

    Args:
        model: The model to create the create operation model from.

    Returns: A create operation model.

    """
    exclude_fields = {"uuid", "created_at"}
    fields: Dict[str, tuple] = {
        **{
            name: (
                field.annotation,
                FieldInfo.from_annotated_attribute(field.annotation, None),
            )
            for name, field in RecordCreateModel.model_fields.items()
            if name not in exclude_fields
        },
        **{
            name: (
                field.annotation,
                FieldInfo.from_annotated_attribute(field.annotation, None),
            )
            for name, field in model.model_fields.items()
            if name not in exclude_fields
        },
    }

    class Config:
        # arbitrary_types_allowed = True
        use_enum_values = True

    return create_model(f"{model.__name__}RecordCreate", **fields, __config__=Config)


def create_record_read_model(model: NodeModel):
    """
    Create a generic model for read operations.

    Args:
        model: The model to create the read operation model from.

    Returns: A read operation model.

    """
    fields: Dict[str, tuple] = {
        **{
            name: (
                field.annotation,
                FieldInfo.from_annotated_attribute(
                    field.annotation, None
                ),  # TODO: eigentlich falsch, read muss alles haben
            )
            for name, field in RecordReadModel.model_fields.items()
        },
        **{
            name: (
                field.annotation,
                FieldInfo.from_annotated_attribute(
                    field.annotation, None
                ),  # TODO: eigentlich falsch, read muss alles haben
            )
            for name, field in model.model_fields.items()
        },
    }

    class Config:
        # arbitrary_types_allowed = True
        from_attributes = True
        use_enum_values = True

    return create_model(f"{model.__name__}RecordRead", **fields, __config__=Config)


class EdgeModel(BaseModel):
    uuid: UUID
    created_at: datetime


class HasRecordCreate(BaseModel):
    start_uuid: UUID
    end_uuid: UUID


class HasRecordRead(EdgeModel, HasRecordCreate):

    class Config:
        from_attributes = True


class HasRecordUpdate(HasRecordCreate): ...


class HasActiveRecordCreate(HasRecordCreate): ...


class HasActiveRecordRead(HasRecordRead): ...


class HasActiveRecordUpdate(HasRecordCreate): ...


class HasPreviousRecordCreate(BaseModel):
    start_uuid: UUID
    end_uuid: UUID


class HasPreviousRecordRead(EdgeModel, HasPreviousRecordCreate):

    class Config:
        from_attributes = True


class HasPreviousRecordUpdate(HasRecordCreate): ...
