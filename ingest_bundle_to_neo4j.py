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


def get_all_process_ids(submission_envelope_id):

    done = False

    url = options.submissionsEnvelopeUuid

    subsEnvUuid = api.getSubmissionEnvelope(ingest_url + "/submissionEnvelopes/" + url)['uuid']['uuid']

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

                if assay_id not in process_ids:
                    process_ids.append(assay_id)

        # if "_links" in files and "next" in files["_links"]:
        #     moreFiles = files["_links"]["next"]["href"]
        #     f = requests.get(moreFiles, "{'Content-type': 'application/json'}")
        #     f.raise_for_status()
        #     files = f.json()
        # else:
        done = True
    return process_ids


def gather_process_data(process_uuid):
    process = api.getEntityByUuid('processes', process_uuid)
    process_info = ex.get_all_process_info(process)
    metadata_by_type = ex.get_metadata_by_type(process_info)
    links = ex.bundle_links(process_info.links)

    for link in links['links']:
        input_options = metadata_by_type[link['input_type']]

        new_inputs = dict()
        for input in link['inputs']:
            current = input_options[input]
            type_id = get_type_and_id(current, link['input_type'])

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
            type_id = get_type_and_id(current, link['output_type'])

            if 'output_specific_type' not in link:
                link['output_specific_type'] = type_id['type']
            elif 'output_specific_type' in link and link['output_specific_type'] !=  type_id['type']:
                print("Outputs of more than one type for process " + process_uuid)

            new_outputs[output] = type_id['id']
        link['outputs'] = new_outputs

    return links


def get_type_and_id(current, type):
    current_type = current['content']['describedBy'].split('/')[-1]

    if type == 'biomaterial':
        current_id = current['content']['biomaterial_core']['biomaterial_id']

    elif type == 'file':
        current_id = current['content']['file_core']['file_name']

    return {'type': current_type, 'id': current_id}


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

    process_uuids = []

    if options.submissionsEnvelopeUuid and not options.processUrl and not options.bundleUuid:
        ingest_url = INGEST_API.replace('{env}', options.system)
        api = ingest.api.ingestapi.IngestApi(ingest_url)

        process_uuids = get_all_process_ids(options.submissionsEnvelopeUuid)


    if  options.submissionsEnvelopeUuid and (options.processUrl or len(process_uuids) > 0):
        if options.processUrl and len(process_uuids) == 0:
            process_uuids.append(options.processUrl)

        output_dir = options.output
        options.ingest = ingest_url
        ex = ingest.exporter.ingestexportservice.IngestExporter(options)
        # neo_loader = Neo4jBundleImporter()

        for process_uuid in process_uuids:
            # dir_name = output_dir + "/" + process_uuid

            linked_graph = gather_process_data(process_uuid)

            directory = os.path.abspath(output_dir)

            if not os.path.exists(directory):
                os.makedirs(directory)

            tmp_file = open(directory + "/" + process_uuid + "_linksGraph.json", "w")
            tmp_file.write(json.dumps(linked_graph['links'], indent=4))
            tmp_file.close()

            # biomaterials = []
            # files = []
            # links_file = None
            # processes = []
            # protocols = []
            # project_file = None
            # for filename in os.listdir(dir_name):
            #     file = dir_name+"/"+filename
            #     with open(file) as f:
            #         content = json.load(f)
            #
            #     if "biomaterial" in content["schema_type"]:
            #         biomaterial_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
            #         biomaterials.append(biomaterial_file)
            #         print(biomaterial_file)
            #
            #     if "file" in content["schema_type"]:
            #         file_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
            #         files.append(file_file)
            #         print(file_file)
            #
            #     if "link_bundle" in content["schema_type"]:
            #         links_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
            #         print(links_file)
            #
            #     if "process" in content["schema_type"]:
            #         process_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
            #         processes.append(process_file)
            #         print(process_file)
            #
            #     if "project" in content["schema_type"]:
            #         project_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
            #         print(project_file)
            #
            #     if "protocol" in content["schema_type"]:
            #         protocol_file = "file:///import/" + dir_name + "/" + urllib.parse.quote(filename)
            #         protocols.append(protocol_file)
            #         print(protocol_file)
            #
            #     # neo_loader.load_data(biomaterials = biomaterials, files = files, processes=processes, protocols =protocols, project_url = project_file, links_url = links_file)

    elif options.bundleUuid:
        dss2neo.main(options.bundleUuid, options.system)
    else:
        print("You must supply a submission envelope UUID and process URL or a bundle URL")
        exit(2)






