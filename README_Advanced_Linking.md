# Human Cell Atlas advanced links generator for graph validation


# Install the packages

Install the basic requirements for the graph analyser by running:

`pip install -r requirements.txt`

The graph analyser relies on the latest version of `ingest-client` rather than the version currently available via pypi. If you haven't already done so, get `ingest-client`:

`git clone git@github.com:HumanCellAtlas/ingest-client.git`

Make sure you have the latest version of the master branch for ingest-client:

`git checkout master`

`git pull origin master`

Now return to the graph analyser directory and run:

`pip install -e path/to/ingest-client`

The same needs to happen for the `graph-diff` package. If you don't already have a local copy, get one:

`git clone git@github.com:hewgreen/graph_diff.git`

and make sure the master branch is up-to-date.

Install the latest version in your graph analyser directory:

`pip install -e path/to/graph-diff`


# Creating extended graph links from ingest

This script creates the modified graph linking json identified at the Cambridge Biohackathon. The script doesn't download entire bundles, it just creates the linking. It does so for all the data in a given submission.

Run the following command. `-e` is the submission envelope (Mongo) ID, `-n` specifies the environment (staging, integration or dev) in which to run the script and `-o` is the directly where the linked graph json files will get written. `-p` is a binary flag - if set, graphs will be rendered (NB - may not work at the moment). `-l` sets the layout option for graphs - only use in conjunction with `-p`; default option is 2.


`./graph_analyser.sh -e 5ba0bd5eb32e850007eb6dd6 -n staging -o output`



