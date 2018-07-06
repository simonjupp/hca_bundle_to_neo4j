# Human Cell Atlas bundle importer for Neo4j

Cypher examples for loading and viewing a bundle as a graph in Neo4j

Start a Neo4j docker instance

`docker run --rm -e NEO4J_AUTH=none -p 7474:7474 -v $PWD/plugins:/plugins -p 7687:7687 neo4j:3.3.3`

Run the follwoing command. `-e` is the submission envelope, `-p` is the full process id URL in ingest (not uuid), `-D` for doing a dry run (doesn't export to blue) and `-o` is the directly where the bundle json files will get written beofre loading into neo4j. 

`bundle_to_neo.sh -e f804f372-6d3e-46d6-ba00-cec3c75122c7  -p http://api.ingest.staging.data.humancellatlas.org/processes/5b3cccc12e12bc00070e1479 -D True -o output`

Go to http://localhost:7474 and run this query `MATCH p=()-->() RETURN p`
