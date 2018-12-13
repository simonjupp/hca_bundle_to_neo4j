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

from argparse import ArgumentParser
import logging
import os
import hca_bundle_neo4j.dss_bundle_to_neo4j as dss2neo
import json

INGEST_API = 'http://api.ingest.{env}.data.humancellatlas.org'
INGEST_API_PROD = 'http://api.ingest.data.humancellatlas.org'


class AdvancedLinksBuilder:

    def __init__(self, options):
        if options.system != 'prod':
            ingest_url = INGEST_API.replace('{env}', options.system)
        else:
            ingest_url = INGEST_API_PROD
        self.api = ingest.api.ingestapi.IngestApi(ingest_url)

        options.ingest = ingest_url
        options.staging = None
        options.dss = None
        self.ex = ingest.exporter.ingestexportservice.IngestExporter(options)

        self.output_dir = options.output

    def get_all_process_ids(self, submission_envelope_id):

        done = False

        url = submission_envelope_id

        process_ids = []
        files = self.api.getFiles(url)

        while not done:

            for file in files['_embedded']['files']:
                if 'sequence_file' in file['content']['describedBy']:
                    derivedFrom = file['_links']['derivedByProcesses']['href']

                    r = requests.get(derivedFrom, "{'Content-type': 'application/json'}")
                    r.raise_for_status()

                    assay = r.json()['_embedded']
                    assay_id = assay['processes'][0]['uuid']['uuid']

                    if assay_id not in process_ids:
                        process_ids.append(assay_id)

            # if "_links" in files and "next" in files["_links"]:
            #     moreFiles = files["_links"]["next"]["href"]
            #     print(moreFiles)
            #     f = requests.get(moreFiles)
            #     f.raise_for_status()
            #     files = f.json()
            # else:
            done = True
        return process_ids


    def gather_process_data(self, process_uuid):
        process = self.api.getEntityByUuid('processes', process_uuid)
        process_info = self.ex.get_all_process_info(process)
        metadata_by_type = self.ex.get_metadata_by_type(process_info)
        links = self.ex.bundle_links(process_info.links)

        for link in links['links']:
            input_options = metadata_by_type[link['input_type']]

            new_inputs = dict()
            for input in link['inputs']:
                current = input_options[input]
                type_id = self.get_type_and_id(current, link['input_type'])

                if 'input_specific_type' not in link:
                    link['input_specific_type'] = type_id['type']
                elif 'input_specific_type' in link and link['input_specific_type'] !=  type_id['type']:
                    print("Inputs of more than one type for process " + process_uuid)

                new_inputs[input] = type_id['id']
            link['inputs'] = new_inputs

            output_options = metadata_by_type[link['output_type']]

            new_outputs = dict()
            for output in link['outputs']:
                current = output_options[output]
                type_id = self.get_type_and_id(current, link['output_type'])

                if 'output_specific_type' not in link:
                    link['output_specific_type'] = type_id['type']
                elif 'output_specific_type' in link and link['output_specific_type'] !=  type_id['type']:
                    print("Outputs of more than one type for process " + process_uuid)

                new_outputs[output] = type_id['id']
            link['outputs'] = new_outputs

        return links


    def get_type_and_id(self, current, type):
        current_type = current['content']['describedBy'].split('/')[-1]

        if type == 'biomaterial':
            current_id = current['content']['biomaterial_core']['biomaterial_id']

        elif type == 'file':
            current_id = current['content']['file_core']['file_name']

        return {'type': current_type, 'id': current_id}


    def _save_file(self, process_uuid, linked_graph):
        directory = os.path.abspath(self.output_dir)

        if not os.path.exists(directory):
            os.makedirs(directory)

        tmp_file = open(directory + "/" + process_uuid + "_linksGraph.json", "w")
        tmp_file.write(json.dumps(linked_graph['links'], indent=4))
        tmp_file.close()

if __name__ == "__main__":

    logging.basicConfig(format=format)

    parser = ArgumentParser()
    parser.add_argument("-b", "--bundle", dest="bundleUuid",
                      help="UUID of a bundle in the DSS")
    parser.add_argument("-n", "--env", dest="system",
                      help="dev, integration, staging or prod", default="dev")
    parser.add_argument("-e", "--subsEnvUuid", dest="submissionsEnvelopeUuid",
                      help="Submission envelope UUID for which to generate the bundle")
    parser.add_argument("-p", "--processUrl", dest="processUrl",
                      help="Process Url")
    parser.add_argument("-D", "--dry", help="do a dry run without submitting to ingest", action="store_true",
                      default=True)
    parser.add_argument("-o", "--output", dest="output",
                      help="output directory where to dump json files submitted to ingest", metavar="FILE")
    parser.add_argument("-l", "--log", help="the logging level", default='INFO')
    parser.add_argument("-v", "--version", dest="schema_version", help="Metadata schema version", default=None)
    parser.add_argument("-i", "--ingest", help="the URL to the ingest API")
    parser.add_argument("-s", "--staging", help="the URL to the staging API")
    parser.add_argument("-d", "--dss", help="the URL to the datastore service")

    options = parser.parse_args()

    biomaterial_file = None
    file_file = None
    project_file = None
    process_file = None
    protocol_file = None
    links_file = None

    process_uuids = []

    # new option to build advanced links files for an entire submission
    if options.submissionsEnvelopeUuid and not options.processUrl and not options.bundleUuid:

        linked_graph_builder = AdvancedLinksBuilder(options)

        process_uuids = linked_graph_builder.get_all_process_ids(options.submissionsEnvelopeUuid)

        for process_uuid in process_uuids:
            linked_graph = linked_graph_builder.gather_process_data(process_uuid)

            linked_graph_builder._save_file(process_uuid, linked_graph)


    # Simon's original code to build a full bundle for a given assay - may or may not still work
    elif  options.submissionsEnvelopeUuid and options.processUrl:
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
            file = dir_name + "/" + filename
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

        neo_loader.load_data(biomaterials=biomaterials, files=files, processes=processes, protocols=protocols,
                             project_url=project_file, links_url=links_file)

    elif options.bundleUuid:
        dss2neo.main(options.bundleUuid, options.system)
    else:
        print("You must supply a submission envelope UUID and process URL or a bundle URL")
        exit(2)






