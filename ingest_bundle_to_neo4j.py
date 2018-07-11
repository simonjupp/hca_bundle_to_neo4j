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

if __name__ == "__main__":

    logging.basicConfig(format=format)

    parser = OptionParser()
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

    if not options.submissionsEnvelopeUuid:
        print ("You must supply a submission envelope UUID")
        exit(2)

    if not options.processUrl:
        print ("You must supply a processUrl")
        exit(2)

    dir_name = options.output

    ex = ingest.exporter.ingestexportservice.IngestExporter(options)

    ex.export_bundle(options.submissionsEnvelopeUuid, options.processUrl)

    biomaterial_file = None
    file_file = None
    project_file = None
    process_file = None
    protocol_file = None
    links_file = None

    for filename in os.listdir(dir_name):

        if "biomaterial" in filename:
            biomaterial_file = "file:///import/"+dir_name+"/"+urllib.parse.quote(filename)
            print (biomaterial_file)

        if "file" in filename:
            file_file = "file:///import/"+dir_name+"/"+urllib.parse.quote(filename)
            print (file_file)

        if "links" in filename:
            links_file = "file:///import/"+dir_name+"/"+urllib.parse.quote(filename)
            print (links_file)

        if "process" in filename:
            process_file = "file:///import/"+dir_name+"/"+urllib.parse.quote(filename)
            print (process_file)

        if "project" in filename:
            project_file = "file:///import/"+dir_name+"/"+urllib.parse.quote(filename)
            print (project_file)

        if "protocol" in filename:
            protocol_file = "file:///import/"+dir_name+"/"+urllib.parse.quote(filename)
            print (protocol_file)



    neo_loader = Neo4jBundleImporter()

    neo_loader.load_data(biomaterial_file, file_file, process_file, protocol_file, project_file, links_file)
