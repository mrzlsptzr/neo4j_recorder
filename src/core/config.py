from dotenv import load_dotenv
import os

# Load the .env file.
load_dotenv()

# Set parameters.
NEO4J_BOLT_PORT = os.getenv("NEO4J_BOLT_PORT")
NEO4J_IP = os.getenv("NEO4J_IP")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
