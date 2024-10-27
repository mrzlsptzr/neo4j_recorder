from neomodel import db, StringProperty, IntegerProperty

from src import init_db
from src.models.neomodel_entities import RecordedNode, NodeRecord
from src.repositories import NodeRepository
from pydantic import Field

from src.services import RecordedNodeService, NodeRecordService
from src.models.pydantic_models import (
    NodeModel,
    create_entity_create_model,
    create_entity_read_model,
    create_entity_update_model,
    create_record_create_model,
    create_record_read_model,
)


# Define pydantic base model and depending crud models
class PersonModel(NodeModel):
    name: str = Field(..., description="The name of the person")
    age: int
    hair_color: str = Field(..., description="The hair color of the person")


PersonCreate = create_entity_create_model(PersonModel)
PersonRead = create_entity_read_model(PersonModel)
PersonRecordCreate = create_record_create_model(PersonModel)
PersonRecordRead = create_record_read_model(PersonModel)
PersonRecordUpdate = create_entity_update_model(PersonModel)


# Define empty neomodel base node and the data containing record node
class Person(RecordedNode): ...


class PersonRecord(NodeRecord):
    name = StringProperty()
    age = IntegerProperty()
    hair_color = StringProperty()


# Define the entity repository
class PersonRepository(NodeRepository[PersonCreate, PersonRead, Person]): ...


# Define the record repository
class PersonRecordRepository(
    NodeRepository[PersonRecordCreate, PersonRecordRead, PersonRecord]
): ...


class PersonService(RecordedNodeService[Person, PersonRecord, PersonRead]): ...


class PersonRecordService(NodeRecordService[PersonRecordRead]): ...


def main():

    person_record_repository = PersonRecordRepository(
        node_model=PersonRecord, read_model=PersonRecordRead
    )
    person_record_service = PersonRecordService(
        repository=person_record_repository, create_model=PersonRecordCreate
    )

    person_repository = PersonRepository(node_model=Person, read_model=PersonRead)
    person_service = PersonService(
        repository=person_repository,
        record_service=person_record_service,
        create_model=PersonCreate,
    )

    person = person_service.create(
        {"name": "Hildegard", "age": 27, "hair_color": "brown"}
    )

    person_service.update(uuid=person.uuid, data={"age": 58})

    person = person_service.read(uuid=person.uuid)

    person_service.delete(uuid=person.uuid)


if __name__ == "__main__":
    init_db()
    db.cypher_query("MATCH (n) DETACH DELETE n")
    main()
