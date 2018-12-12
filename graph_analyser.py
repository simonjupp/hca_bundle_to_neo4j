import json

from ingest_bundle_to_neo4j import AdvancedLinksBuilder
from argparse import ArgumentParser
import graph_diff as gf
import os

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("-n", "--env", dest="system",
                        help="dev, integration, staging or prod", default="dev")
    parser.add_argument("-e", "--subsEnvUuid", dest="submissionsEnvelopeUuid",
                        help="Submission envelope UUID for which to generate the bundle")
    parser.add_argument("-D", "--dry", help="do a dry run without submitting to ingest", action="store_true",
                        default=True)
    parser.add_argument("-o", "--output", dest="output",
                        help="output directory where to dump json files submitted to ingest", metavar="FILE")
    parser.add_argument("-p", "--plot", action="store_true",
                        help="Flag to draw the graphs")
    parser.add_argument("-l", "--layout", dest="layout",
                        help="Graph layout option", default="2")

    options = parser.parse_args()

    process_uuids = []

    if options.submissionsEnvelopeUuid:
        linked_graph_builder = AdvancedLinksBuilder(options)

        process_uuids = linked_graph_builder.get_all_process_ids(options.submissionsEnvelopeUuid)

        print("About to deal with " + str(len(process_uuids)) + " processes")


        for process_uuid in process_uuids:
            linked_graph = linked_graph_builder.gather_process_data(process_uuid)

            linked_graph_builder._save_file(process_uuid, linked_graph)


        l = os.listdir(options.output)
        infiles = [options.output + "/" + x for x in l]
        print('Processing {} bundles...'.format(len(infiles)))

        feature_list = []
        assumption_list = []
        graphs = []

        for infile in infiles:
            with open(infile) as f:
                data = json.load(f)
                graph = gf.load_graph_networkx(data)
                G = graph[0]
                node_names = graph[1]
                if options.plot:
                    gf.plot_graph(G, node_names, infile, options.layout, save_fig=False)
                G_features = gf.graph_stats(G)
                feature_list.append(G_features)

                # Assess graph assumptions
                G_assumptions = gf.graph_assumptions(G)
                assumption_list.append(G_assumptions)

            graphs.append(G)

        # load_graph_neo4j(data)
        gf.generate_report(feature_list, assumption_list)
        gf.graph_compare(graphs)

    else:
        print("You must supply a submission envelope UUID and process URL or a bundle URL")
        exit(2)
