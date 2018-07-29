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
    MERGE (n:biomaterial {document_id : materials.hca_ingest.document_id})
    SET n.content = apoc.convert.toJson(materials);
"""

file_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.files) as file
MERGE (n:file {document_id : file.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(file);
"""

process_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.processes) as process
MERGE (n:process {document_id : process.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(process);

"""

protocol_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.protocols) as protocol
MERGE (n:protocol {document_id : protocol.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(protocol);
"""

project_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:project {document_id : value.hca_ingest.document_id})
SET n.content = apoc.convert.toJson(value);

"""

links_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
UNWIND (value.links) as links
MERGE (p:process { document_id: links.process})
WITH p, links.inputs as inputs, links.outputs as outputs, links.protocols as protocols
FOREACH (i in inputs | MERGE (input {document_id : i}) Merge (p)-[:LINK { name : "has_input"}]->(input))
FOREACH (o in outputs | MERGE (output {document_id : o}) Merge (p)-[:LINK { name : "has_output"}]->(output))
FOREACH (prot in protocols | MERGE (protocol {document_id : prot.protocol_id}) Merge (p)-[:LINK { name : "has_protocol"}]->(protocol))
"""

node_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:%s {document_id : \"%s\"})
SET n.content = apoc.convert.toJson(value);

"""
class Neo4jBundleImporter:


    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687")

        session = self.driver.session()

        session.run("CREATE CONSTRAINT ON (i:project) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:biomaterial) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:file) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:process) ASSERT i.document_id IS UNIQUE;")
        session.run("CREATE CONSTRAINT ON (i:protocol) ASSERT i.document_id IS UNIQUE;")

        session.close()

    def load_node(self, url, type, uuid):
        session = self.driver.session()
        session.run(node_load % (url,type, uuid ))
        session.close()

    def load_links(self, url):
        session = self.driver.session()
        session.run(links_load % (url))
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




