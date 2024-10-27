from src import init_db
from src.services import ServiceFactory
from src.models import NodeModel, NodeRecord
from pydantic import Field, String
from neomodel import StringProperty, IntegerProperty


class PersonModel(NodeModel):
    name: str = Field(..., description="The name of the person")
    age: int
    hair_color: str = Field(..., description="The hair color of the person")


class PersonRecord(NodeRecord):
    name = StringProperty()
    age = IntegerProperty()
    hair_color = StringProperty()


def main():

    # Generating the PersonService through the factory
    person_service = ServiceFactory.create_service(PersonModel, PersonRecord)

    # Using the generated service
    person = person_service.create(
        {"name": "Hildegard", "age": 27, "hair_color": "brown"}
    )
    person_service.update(uuid=person.uuid, data={"age": 58})
    person = person_service.read(uuid=person.uuid)
    person_service.delete(uuid=person.uuid)


if __name__ == "__main__":
    init_db()
    main()
