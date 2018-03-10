# Human Cell Atlas bundle importer for Neo4j

Cypher examples for loading and viewing a bundle as a graph in Neo4j

Start a Neo4j docker instance

`docker run --rm -e NEO4J_AUTH=none -p 7474:7474 -v $PWD/plugins:/plugins -p 7687:7687 neo4j:3.3.3`

Go to http://localhost:7474

Run the commands in bundle_loading_cypher.txt
