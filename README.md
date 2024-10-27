# Neo4j Recorder

The neo4j recorder can record changes of nodes and edges.

## Node records

The recorder creates a node record for each change of the node data. The node is connected by a HAS_RECORD relationships to its node records. The node is connected by a HAS_ACTIVE_RECORD relationship to the currently active record node. Each node record has a HAS_PREVIOUS_RECORD relationship to its previous record node.

## Edge records

The recorder creates a edge record for each change of the edge data. The edge record is connected to both nodes of the recorded relationship. The relationships between the edge record and the nodes are named RECORDED__{relationship} and {relationship}__RECORDED. Each edge record has a HAS_PREVIOUS_RECORD relationship to ist previous record node.

# HowTo

(...coming...)