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
    MERGE (n:biomaterial {document_id : value.provenance.document_id})
    SET n.content = apoc.convert.toJson(value);
"""

file_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:file {document_id : value.provenance.document_id})
SET n.content = apoc.convert.toJson(value);
"""

process_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:process {document_id : value.provenance.document_id})
SET n.content = apoc.convert.toJson(value);

"""

protocol_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:protocol {document_id : value.provenance.document_id})
SET n.content = apoc.convert.toJson(value);
"""

project_load = """
WITH \"%s\" as url
CALL apoc.load.json(url) yield value
MERGE (n:project {document_id : value.provenance.document_id})
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

    def load_data(self, biomaterials=None, files=None, processes=None, protocols=None, project_url=None, links_url=None):
        session = self.driver.session()

        for biomaterial_url in biomaterials:
            print (biomaterial_load % (biomaterial_url))
            session.run(biomaterial_load % (biomaterial_url))

        for file_url in files:
            print(file_load % (file_url))
            session.run(file_load % (file_url))

        for process_url in processes:
            print(process_load % (process_url))
            session.run(process_load % (process_url))

        for protocol_url in protocols:
            print(protocol_load % (protocol_url))
            session.run(protocol_load % (protocol_url))

        if project_url:
            print(project_load % (project_url))
            session.run(project_load % (project_url))

        if links_url:
            print(links_load % (links_url))
            session.run(links_load % (links_url))

        session.close()



if __name__ == '__main__':
    Neo4jBundleImporter()




