#!/usr/bin/env python
"""
Description goes here
"""
import ingest.exporter.ingestexportservice
import ingest.api.ingestapi
import requests

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

INGEST_API = 'http://api.ingest.{env}.data.humancellatlas.org'

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
        ingest_url = INGEST_API.replace('{env}', options.system)
        api = ingest.api.ingestapi.IngestApi(ingest_url)

        done = False

        url = options.submissionsEnvelopeUuid
        process_ids = []
        files = api.getFiles(url)

        while not done:

            for file in files['_embedded']['files']:
                if 'sequence_file' in file['content']['describedBy']:
                    derivedFrom = file['_links']['derivedByProcesses']['href']

                    r = requests.get(derivedFrom, "{'Content-type': 'application/json'}")
                    r.raise_for_status()

                    assay = r.json()['_embedded']
                    assay_id = assay['processes'][0]['uuid']['uuid']
                    process_ids.append(assay_id)

            if "_links" in files and "next" in files["_links"]:
                moreFiles = files["_links"]["next"]["href"]
                f = requests.get(moreFiles, "{'Content-type': 'application/json'}")
                f.raise_for_status()
                files = f.json()
            else:
                done = True




    if  options.submissionsEnvelopeUuid and (options.processUrl or len(process_ids) > 0):
        if options.processUrl and len(process_ids) == 0:
            process_ids.append(options.processUrl)

        output_dir = options.output
        ex = ingest.exporter.ingestexportservice.IngestExporter(options)
        neo_loader = Neo4jBundleImporter()

        for process_id in process_ids:
            print(process_id)

            dir_name = output_dir + "/" + process_id
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

                neo_loader.load_data(biomaterials = biomaterials, files = files, processes=processes, protocols =protocols, project_url = project_file, links_url = links_file)

    elif options.bundleUuid:
        dss2neo.main(options.bundleUuid, options.system)
    else:
        print("You must supply a submission envelope UUID and process URL or a bundle URL")
        exit(2)






