#!/usr/bin/env python
"""
Description goes here
"""
from hca_bundle_neo4j.neo4j_loader import Neo4jBundleImporter

__author__ = "jupp"
__license__ = "Apache 2.0"
__date__ = "21/03/2018"

import requests
import sys
import re

# DSS_DOMAIN = "dss"
# HCA_DOMAIN = "dev.data.humancellatlas.org"


def get_bundle(bundle_uuid, env):
    bundle_url = "https://dss.{}.data.humancellatlas.org/v1/bundles/{}?replica=aws".format(env, bundle_uuid)
    r = requests.get(bundle_url)
    return r.json()


def get_file_url(file_uuid, env):
    file_url = "https://dss.{}.data.humancellatlas.org/v1/files/{}".format(env, file_uuid)
    return "{}{}".format(file_url, '?replica=aws')


def bundle_to_graph(bundle, env):
    neoBundleImporter = Neo4jBundleImporter()

    for file in bundle['bundle']['files']:
        if "dcp-type=\"metadata/" in file['content-type']:
            m = re.search( "metadata/([^\"]*)",  file['content-type'])

            url = get_file_url(file['uuid'], env)
            if m.group(1) == "links":
                neoBundleImporter.load_links(url)
            else:
                print(m.group(1) + " " + url)
                neoBundleImporter.load_node(url, m.group(1), file['uuid'])



def bundle_to_rdf(bundle):
    bundle_uuid = bundle['bundle']['uuid']
    g = bundle_to_graph(bundle)
    g.serialize(destination="{}.ttl".format(bundle_uuid), format='ttl')
    print("Wrote file: {}.ttl".format(bundle_uuid))
    return "{}.ttl".format(bundle_uuid)


def main(bundle_uuid, env):

    bundle = get_bundle(bundle_uuid, env)
    bundle_to_graph(bundle, env)


if __name__ == "__main__":
    print(sys.argv)
    main(sys.argv[-2:][0], sys.argv[-2:][1])
