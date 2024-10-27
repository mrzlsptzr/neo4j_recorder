from src.repositories import NodeRepository
from src.services import RecordedNodeService, NodeRecordService
from src.models.pydantic_models import (
    create_entity_create_model,
    create_entity_read_model,
    create_entity_update_model,
    create_record_create_model,
    create_record_read_model,
)


class ServiceFactory:
    """
    Factory class for dynamically generating service instances.
    """

    @staticmethod
    def create_service(model_class, node_class, record_class):
        # Dynamic generation of CRUD models
        create_model = create_entity_create_model(model_class)
        read_model = create_entity_read_model(model_class)
        update_model = create_entity_update_model(model_class)
        record_create_model = create_record_create_model(model_class)
        record_read_model = create_record_read_model(model_class)

        # Creating the generic repositories
        class GenericRepository(NodeRepository[create_model, read_model, node_class]):
            pass

        class GenericRecordRepository(
            NodeRepository[record_create_model, record_read_model, record_class]
        ):
            pass

        # Creating the generic services
        class GenericService(RecordedNodeService[node_class, record_class, read_model]):
            pass

        class GenericRecordService(NodeRecordService[record_read_model]):
            pass

        # Initialization of repository and service instances
        record_repository = GenericRecordRepository(
            node_model=record_class, read_model=record_read_model
        )
        record_service = GenericRecordService(
            repository=record_repository, create_model=record_create_model
        )

        repository = GenericRepository(node_model=node_class, read_model=read_model)
        service = GenericService(
            repository=repository,
            record_service=record_service,
            create_model=create_model,
        )

        return service
