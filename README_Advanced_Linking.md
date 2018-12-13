# Human Cell Atlas advanced links generator for graph validation


# Install the packages

`pip install -r requirements.txt`



# Creating extended graph links from ingest

The version of the script creates the modified graph linking json identified at the Cambridge Biohackathon. The script doesn't download entire bundles, it just creates the linking. It does so for all the data in a given submission.

Run the following command. `-e` is the submission envelope (Mongo) ID, `-n` specifies the environment (staging, integration or dev) in which to run the script and `-o` is the directly where the linked graph json files will get written.

`./bundle_to_neo.sh -e 5ba0bd5eb32e850007eb6dd6 -n staging -o output`


# Validating graphs

some stuff here
