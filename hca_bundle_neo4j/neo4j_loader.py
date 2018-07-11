#!/usr/bin/env python
"""
Description goes here
"""
__author__ = "jupp"
__license__ = "Apache 2.0"
__date__ = "06/07/2018"

import sys
from neo4j.v1 import GraphDatabase, basic_auth

biomaterial_load = """
    WITH \"%s\" as url
    CALL apoc.load.json(url) yield value
    UNWIND (value.biomaterials) as materials
    MERGE (n:Biomaterial {document_id : materials.hca_ingest.document_id})
    SET n.content = apoc.convert.toJson(materials);
"""

file_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.files) as file
MERGE (n:File {document_id : file.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(file);
"""

process_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.processes) as process
MERGE (n:Process {document_id : process.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(process);

"""

protocol_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.protocols) as protocol
MERGE (n:Protocol {document_id : protocol.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(protocol);
"""

project_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:Project {document_id : value.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(value);

"""

links_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.links) as links
MATCH (source {document_id : links.source_id}), (target {document_id : links.destination_id})
WITH source, target, links.destination_type as rel
MERGE (source)-[:LINK { name : rel}]->(target);
"""

class Neo4jBundleImporter:


    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687")

        session = self.driver.session()

        session.run("CREATE CONSTRAINT ON (i:Project) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:Biomaterial) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:File) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:Process) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:Protocol) ASSERT i.document_id IS UNIQUE;")

        session.close()

    def load_data(self, biomaterial_url, file_url, process_url, protocol_url, project_url, links_url):
        session = self.driver.session()

        print (biomaterial_load % (biomaterial_url))
        session.run(biomaterial_load % (biomaterial_url))
        session.run(file_load % (file_url))
        session.run(process_load % (process_url))
        session.run(protocol_load % (protocol_url))
        session.run(project_load % (project_url))
        session.run(links_load % (links_url))

        session.close()



if __name__ == '__main__':
    Neo4jBundleImporter()




