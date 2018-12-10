#!/usr/bin/env python
"""
Description goes here
"""
import ingest.exporter.ingestexportservice

from hca_bundle_neo4j.neo4j_loader import Neo4jBundleImporter
import urllib.parse
__author__ = "jupp"
__license__ = "Apache 2.0"
__date__ = "06/07/2018"

from optparse import OptionParser
import logging
import os
import hca_bundle_neo4j.dss_bundle_to_neo4j as dss2neo
import json

if __name__ == "__main__":

    logging.basicConfig(format=format)

    parser = OptionParser()
    parser.add_option("-b", "--bundle", dest="bundleUuid",
                      help="UUID of a bundle in the DSS")
    parser.add_option("-n", "--env", dest="system",
                      help="dev, integration, staging or prod", default="dev")
    parser.add_option("-e", "--subsEnvUuid", dest="submissionsEnvelopeUuid",
                      help="Submission envelope UUID for which to generate the bundle")
    parser.add_option("-p", "--processUrl", dest="processUrl",
                      help="Process Url")
    parser.add_option("-D", "--dry", help="do a dry run without submitting to ingest", action="store_true",
                      default=True)
    parser.add_option("-o", "--output", dest="output",
                      help="output directory where to dump json files submitted to ingest", metavar="FILE")
    parser.add_option("-l", "--log", help="the logging level", default='INFO')
    parser.add_option("-v", "--version", dest="schema_version", help="Metadata schema version", default=None)
    parser.add_option("-i", "--ingest", help="the URL to the ingest API")
    parser.add_option("-s", "--staging", help="the URL to the staging API")
    parser.add_option("-d", "--dss", help="the URL to the datastore service")

    (options, args) = parser.parse_args()

    biomaterial_file = None
    file_file = None
    project_file = None
    process_file = None
    protocol_file = None
    links_file = None

    if options.submissionsEnvelopeUuid and not options.processUrl:
        

    if  options.submissionsEnvelopeUuid and options.processUrl:

        dir_name = options.output
        ex = ingest.exporter.ingestexportservice.IngestExporter(options)

        ex.export_bundle(options.submissionsEnvelopeUuid, options.processUrl)

        biomaterials = []
        files = []
        links_file = None
        processes = []
        protocols = []
        project_file = None
        for filename in os.listdir(dir_name):
            file = dir_name+"/"+filename
            with open(file) as f:
                content = json.load(f)

            if "biomaterial" in content["schema_type"]:
                biomaterial_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
                biomaterials.append(biomaterial_file)
                print(biomaterial_file)

            if "file" in content["schema_type"]:
                file_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
                files.append(file_file)
                print(file_file)

            if "link_bundle" in content["schema_type"]:
                links_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
                print(links_file)

            if "process" in content["schema_type"]:
                process_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
                processes.append(process_file)
                print(process_file)

            if "project" in content["schema_type"]:
                project_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
                print(project_file)

            if "protocol" in content["schema_type"]:
                protocol_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
                protocols.append(protocol_file)
                print(protocol_file)

        neo_loader = Neo4jBundleImporter()

        neo_loader.load_data(biomaterials = biomaterials, files = files, processes=processes, protocols =protocols, project_url = project_file, links_url = links_file)

    elif options.bundleUuid:
        dss2neo.main(options.bundleUuid, options.system)
    else:
        print("You must supply a submission envelope UUID and process URL or a bundle URL")
        exit(2)






