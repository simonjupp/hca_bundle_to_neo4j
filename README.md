# Human Cell Atlas bundle importer for Neo4j

Scripts for loading a bundle from ingest or the HCA datastore into Neo4j. 

![Bundle graph in neo4j](bundle_neo4j.jpg?raw=true)

# Install the packages

`pip install -r requirements.txt`

Start a Neo4j docker instance

`docker run --rm -e NEO4J_AUTH=none -e NEO4J_apoc_import_file_enabled=true -p 7474:7474 -v $PWD/plugins:/plugins -v $PWD:/import -p 7687:7687 neo4j:3.3.3`

# Loading a bundle from the datastore

Provide the bundle UUID and the environment (dev, integration or staging)

`./bundle_to_neo.sh -b f804f372-6d3e-46d6-ba00-cec3c75122c7  -n integration`

# Creating a bundle from ingest

You'll need access to the latest hca-ingest libraries. If you've run this before do `pip uninstall hca-ingest` to remove the old ingest client. Then checkout
the ingest library from https://github.com/HumanCellAtlas/ingest-client. To install the latest ingest client do `pip install -e <path to ingest-client>`

Run the following command. `-e` is the submission envelope uuid, `-p` is the assay process uuid (this must be the final sequencing process uuid), `-D` for doing a dry run (doesn't export to blue) and `-o` is the directly where the bundle json files will get written beofre loading into neo4j.

`./bundle_to_neo.sh -e 86243a5a-b869-4da3-b97f-759ba26b0e2c -p afd5ad73-353b-4d04-b045-15736f7cf53c -D True -o output`

# Query neo4j

Go to http://localhost:7474 and run this query `MATCH p=()-->() RETURN p`
