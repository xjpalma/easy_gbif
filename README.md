# GBIF Local Management #
---
This repository is an attempt to create a simple script in python to manage the pygbif API (https://github.com/sckott/pygbif).

## Minimum system requirements:
Install the following softwares:
* **python**: https://www.python.org/
* **pygbif module**: ``pip install pygbif``

## Modules
At the moment, only occurence module is available. Hope soon Registry and Species modules will be available. Note that GBIF maps API is not included in pygbif. 

## Occurrences  module API:
* **search** - Search GBIF occurrences
* **get** - Gets details for a single, interpreted occurrence
* **get_verbatim** - Gets a verbatim occurrence record without any interpretation
* **get_fragment** - Get a single occurrence fragment in its raw form (xml or json)
* **count** - Returns occurrence counts for a predefined set of dimensions
* **count_basisofrecord** - Lists occurrence counts by basis of record.
* **count_year** - Lists occurrence counts by year
* **count_datasets** - Lists occurrence counts for datasets that cover a given taxon or country
* **count_countries** - Lists occurrence counts for all countries covered by the data published by the given country
* **count_schema** - List the supported metrics by the service
* **count_publishingcountries** - Lists occurrence counts for all countries that publish data about the given country
* **download** - Spin up a download request for GBIF occurrence data.
* **download_meta** - Retrieves the occurrence download metadata by its unique key. Further named arguments passed on to requests.get can be included as additional arguments
* **download_list** - Lists the downloads created by a user.
* **download_get** - Get a download from GBIF.

## Help, Bugs, Feedback
If you need help, do not bother me. To report bugs, please contact jorgempalma@tecnico.ulisboa.pt

## License
GNU General Public License. See the [GNU General Public License](http://www.gnu.org/copyleft/gpl.html) web page for more information.