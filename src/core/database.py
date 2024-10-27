from .config import NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_IP, NEO4J_BOLT_PORT
from neomodel import config


def init_db():
    config.DATABASE_URL = (
        f"bolt://{NEO4J_USERNAME}:{NEO4J_PASSWORD}@{NEO4J_IP}:{NEO4J_BOLT_PORT}"
    )
