# Harvest System Proposal

This proposal describes Harvester Service for the GeoLink project.

The Harvest Service retrieves RDF dumps of the datasets from a set of providers and ingests the triples from each RDF dump into separate named graphs in a single triple store.
The named graphs are then exposed via a SPARQL endpoint for further processing.

## Harvesting From Member Repositories

**What exactly will be located at each member repository?**

Each provider maintains a complete dump and may optionally maintain a partial dump of their datasets which contains only datasets that have been updated since the Harvest Service last retrieved the provider's partial dump.
Maintaining a partial dump is recommended for providers whose data holdings may change often and/or contain a large number of triples (most of which do not change often).
Each dump file must be made publicly accessible over HTTP.

Providers also maintain a [VoID file](http://www.w3.org/TR/void/#void-file) at their site which contains a description of their full dump and optionally their partial dump.
Two example VoID files illustrate the structure of a VoID file for (1) a provider publishing a full dump and (2) a provider publishing both full and partial dumps of their datasets.

Scenario 1: Provider publishing a full dump of their datasets in Turtle format:

```{ttl}
@prefix void: <http://rdfs.org/ns/void#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix : <#> .

:#d1lodfull a void:Dataset ;
  dcterms:title "DataOne Full Dump" ;
  dcterms:description "A Linked Open Data graph of the holdings in DataOne produced for the GeoLink project." ;
  void:feature <http://www.w3.org/ns/formats/Turtle> ;
  void:feature <http://lod.dataone.org/glharvest#FullDump> ;
  void:dataDump <http://lod.dataone.org/dataone.ttl> ;
  dcterms:modified "2015-11-05"^^xsd:date ;
  .
```

Scenario 2: Provider publishing a full and partial dump of their datasets, both in Turtle format:

```{ttl}
@prefix void: <http://rdfs.org/ns/void#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix : <#> .

:#d1lodfull a void:Dataset ;
  dcterms:title "DataOne Full Dump" ;
  dcterms:description "A Linked Open Data graph of the holdings in DataOne produced for the GeoLink project." ;
  void:feature <http://www.w3.org/ns/formats/Turtle> ;
  void:feature <http://lod.dataone.org/glharvest#FullDump> ;
  void:dataDump <http://lod.dataone.org/dataone.ttl> ;
  dcterms:modified "2015-11-05"^^xsd:date ;
  .

:#d1lodpartial a void:Dataset ;
  dcterms:title "DataOne Partial Dump" ;
  dcterms:description "A partial Linked Open Data graph of the holdings in DataOne produced for the GeoLink project." ;
  void:feature <http://www.w3.org/ns/formats/Turtle> ;
  void:feature <http://lod.dataone.org/glharvest#PartialDump> ;
  void:dataDump <http://lod.dataone.org/dataone.ttl> ;
  dcterms:modified "2015-11-05"^^xsd:date ;
  .
```

Note the use of `<http://lod.dataone.org/glharvest#FullDump>` and `<http://lod.dataone.org/glharvest#PartialDump>`.
These are `void:TechnicalFeature`s described in a custom ontology hosted at `<http://lod.dataone.org/glharvest>` which describe the concept of full and partial dumps, respectively.

The [VoID spec](http://www.w3.org/TR/void/) describes other properties that may be added to the VoID file such as `foaf:homepage` or `dcterms:publisher`.
These properties may be specified in the VoID file but are not specifically needed for the Harvest System.


**How will harvesting be coordinated?**

The Harvest System maintains a list of URIs for each provider's VoID file in a single registry file that is manually updated in order to register a new provider with the service.
Along with the URI for the VoID file, the most recent `dcterms:modified` value for the the dump (full or partial) is saved and only dumps with a modification date after this value are harvested.

Harvesting is conducted every 24 hours by parsing the URIs from the registry file and adding each URI to a queue.

When an item in the queue is processed, the Harvest System:

- Visits the VoID file given by the URI
- Parses the VoID file to determine the type, location, and last modified date of the dump
- Checks the `dcterms:modified` value with the stored value

If the dump hasn't been updated since the last visit, no work is done and the next item in the queue, if any, is processed.
If the dump has been been updated since the last visit, the Harvest System:

- Stores the last modified date of the dump in the registry file
- Copies the dump from the provider to the Harvest System
- Processes the dump (described below)

**How will the the triples be processed?**

If the dump is a full dump and a partial dump is not made available at the provider, all triples in the provider's named graph are removed and replaced with the triples
from the retrieved dump.

If the dump is a partial dump, the Harvest System imports the triples from the dump into a temporary named graph, queries the named graph for the unique set of subjects of the triples in the temporary named graph and deletes any triples in the provider's named graph that have those subjects.
Then the triples from the temporary named graph are copied directly into the provider's named graph.

## SPARQL Endpoint

The set of named graphs in the central triple store are available via a SPARQL endpoint and a corresponding [SPARQL Service Description](http://www.w3.org/TR/sparql11-service-description/#sd-Dataset) file that describes the datasets held in the central triple store.
The SPARQL service description is used by other groups to perform co-referenced resolution and other forms of post-processing.

## Infrastructure

The Harvest System runs on a single virtual machine hosted at UCSB which runs
the following pieces of software:

- Triple store: [GraphDB](http://graphdb.ontotext.com/display/GraphDB6/Home)
- Harvester: Python package
- Queueing system: Python-based [RQ](http://python-rq.org/) queue running [http://redis.io/](http://redis.io/)
- SPARQL Endpoint: [Virtuoso](virtuoso.openlinksw.com)
