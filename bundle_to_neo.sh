
echo "Starting docker..."

docker run --rm -e NEO4J_AUTH=none -e NEO4J_apoc_import_file_enabled=true -p 7474:7474 -v $PWD/plugins:/plugins -v $PWD:/import -p 7687:7687 neo4j:3.3.3

python hca_bundle_neo4j/ingest_bundle_to_neo4j.py $@

