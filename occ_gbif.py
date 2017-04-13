#!/usr/bin/python
#-*- coding: utf-8 -*-

'''
source: https://github.com/sckott/pygbif

REGISTRY module API:
   organizations   nodes   networks   installations   datasets
                                                      dataset_metrics
                                                      dataset_suggest
                                                      dataset_search
                                                      
SPECIES module API:
   name_backbone
   name_suggest
   name_usage
   name_lookup
   name_parser
   
OCCURENCES module API:
   search   get            count                      download
            get_verbatim   count_basisofrecord        download_meta
            get_fragment   count_year                 download_list
                           count_datasets             download_get
                           count_countries
                           count_schema
                           count_publishingcountries
'''

import sys
import os
import argparse
import traceback
import json
from pygbif import occurrences as occ
from pygbif import registry
from pygbif import species

os.environ['GBIF_USER']  = 'jpalma'
os.environ['GBIF_PWD']   = 'lNi95cKZ@'
os.environ['GBIF_EMAIL'] = 'jorgempalma@tecnico.ulisboa.pt'

def get_parser():
    '''Get parser object'''
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='A program to manage gbif occurence module')
    
    ### SEARCH ###
    parser.add_argument('-s', '--search',
                        nargs=2,
                        dest='search',
                        help='Search GBIF occurrences',
                        required=False,
                        action='append')
    '''                 Parameters:
                            taxonKey – [int] A GBIF occurrence identifier
                            q – [str] Simple search parameter. The value for this parameter can be a simple word or a phrase.
                            spellCheck – [bool] If True ask GBIF to check your spelling of the value passed to the search parameter. IMPORTANT: This only checks the input to the search parameter, and no others. Default: False
                            repatriated – [str] Searches for records whose publishing country is different to the country where the record was recorded in
                            kingdomKey – [int] Kingdom classification key
                            phylumKey – [int] Phylum classification key
                            classKey – [int] Class classification key
                            orderKey – [int] Order classification key
                            familyKey – [int] Family classification key
                            genusKey – [int] Genus classification key
                            subgenusKey – [int] Subgenus classification key
                            scientificName – [str] A scientific name from the GBIF backbone. All included and synonym taxa are included in the search.
                            datasetKey – [str] The occurrence dataset key (a uuid)
                            catalogNumber – [str] An identifier of any form assigned by the source within a physical collection or digital dataset for the record which may not unique, but should be fairly unique in combination with the institution and collection code.
                            recordedBy – [str] The person who recorded the occurrence.
                            collectionCode – [str] An identifier of any form assigned by the source to identify the physical collection or digital dataset uniquely within the text of an institution.
                            institutionCode – [str] An identifier of any form assigned by the source to identify the institution the record belongs to. Not guaranteed to be que.
                            country – [str] The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded. See here http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
                            basisOfRecord – [str] Basis of record, as defined in our BasisOfRecord enum here http://gbif.github.io/gbif-api/apidocs/org/gbif/api/vocabulary/BasisOfRecord.html Acceptable values are:
                                FOSSIL_SPECIMEN An occurrence record describing a fossilized specimen.
                                HUMAN_OBSERVATION An occurrence record describing an observation made by one or more people.
                                LITERATURE An occurrence record based on literature alone.
                                LIVING_SPECIMEN An occurrence record describing a living specimen, e.g.
                                MACHINE_OBSERVATION An occurrence record describing an observation made by a machine.
                                OBSERVATION An occurrence record describing an observation.
                                PRESERVED_SPECIMEN An occurrence record describing a preserved specimen.
                                UNKNOWN Unknown basis for the record.
                            eventDate – [date] Occurrence date in ISO 8601 format: yyyy, yyyy-MM, yyyy-MM-dd, or MM-dd. Supports range queries, smaller,larger (e.g., 1990,1991, whereas 1991,1990 wouldn’t work)
                            year – [int] The 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries, smaller,larger (e.g., 1990,1991, whereas 1991,1990 wouldn’t work)
                            month – [int] The month of the year, starting with 1 for January. Supports range queries, smaller,larger (e.g., 1,2, whereas 2,1 wouldn’t work)
                            q – [str] Query terms. The value for this parameter can be a simple word or a phrase.
                            decimalLatitude – [float] Latitude in decimals between -90 and 90 based on WGS 84. Supports range queries, smaller,larger (e.g., 25,30, whereas 30,25 wouldn’t work)
                            decimalLongitude – [float] Longitude in decimals between -180 and 180 based on WGS 84. Supports range queries (e.g., -0.4,-0.2, whereas -0.2,-0.4 wouldn’t work).
                            publishingCountry – [str] The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded.
                            elevation – [int/str] Elevation in meters above sea level. Supports range queries, smaller,larger (e.g., 5,30, whereas 30,5 wouldn’t work)
                            depth – [int/str] Depth in meters relative to elevation. For example 10 meters below a lake surface with given elevation. Supports range queries, smaller,larger (e.g., 5,30, whereas 30,5 wouldn’t work)
                            geometry – [str] Searches for occurrences inside a polygon described in Well Known Text (WKT) format. A WKT shape written as either POINT, LINESTRING, LINEARRING POLYGON, or MULTIPOLYGON. Example of a polygon: ((30.1 10.1, 20, 20 40, 40 40, 30.1 10.1)) would be queried as http://bit.ly/1BzNwDq.
                            hasGeospatialIssue – [bool] Includes/excludes occurrence records which contain spatial issues (as determined in our record interpretation), i.e. hasGeospatialIssue=TRUE returns only those records with spatial issues while hasGeospatialIssue=FALSE includes only records without spatial issues. The absence of this parameter returns any record with or without spatial issues.
                            issue – [str] One or more of many possible issues with each occurrence record. See Details. Issues passed to this parameter filter results by the issue.
                            hasCoordinate – [bool] Return only occurence records with lat/long data (true) or all records (false, default).
                            typeStatus – [str] Type status of the specimen. One of many options. See ?typestatus
                            recordNumber – [int] Number recorded by collector of the data, different from GBIF record number. See http://rs.tdwg.org/dwc/terms/#recordNumber} for more info
                            lastInterpreted – [date] Date the record was last modified in GBIF, in ISO 8601 format: yyyy, yyyy-MM, yyyy-MM-dd, or MM-dd. Supports range queries, smaller,larger (e.g., 1990,1991, whereas 1991,1990 wouldn’t work)
                            continent – [str] Continent. One of africa, antarctica, asia, europe, north_america (North America includes the Caribbean and reachies down and includes Panama), oceania, or south_america
                            fields – [str] Default (all) returns all fields. minimal returns just taxon name, key, latitude, and longitude. Or specify each field you want returned by name, e.g. fields = c('name','latitude','elevation').
                            mediatype – [str] Media type. Default is NULL, so no filtering on mediatype. Options: NULL, MovingImage, Sound, and StillImage
                            limit – [int] Number of results to return. Default: 300
                            offset – [int] Record to start at. Default: 0
                            facet – [str] a character vector of length 1 or greater
                            establishmentMeans – [str] EstablishmentMeans, possible values include: INTRODUCED, INVASIVE, MANAGED, NATIVE, NATURALISED, UNCERTAIN
                            facetMincount – [int] minimum number of records to be included in the faceting results
                            facetMultiselect – [bool] Set to true to still return counts for values that are not currently filtered. See examples. Default: false  '''


    ### GET ###
    parser.add_argument('-g', '--get',
                        nargs=1,
                        dest='get',
                        help='Gets details for a single, interpreted occurrence',
                        required=False,
                        type=int,
                        action='store')
    '''                 Parameters:
                            key – [int] A GBIF occurrence key  '''
    
    parser.add_argument('-gv', '--get_verbatim',
                        nargs=1,
                        dest='get_verbatim',
                        help='Gets a verbatim occurrence record without any interpretation',
                        required=False,
                        type=int,
                        action='store')
    '''                 Parameters:
                            key – [int] A GBIF occurrence key  '''
                            
    parser.add_argument('-gf', '--get_fragment',
                        nargs=1,
                        dest='get_fragment',
                        help='Get a single occurrence fragment in its raw form (xml or json)',
                        required=False,
                        type=int,
                        action='store')
    '''                 Parameters:
                            key – [int] A GBIF occurrence key  '''

    
    ### COUNT ###
    parser.add_argument('-c', '--count',
                        nargs=2,
                        dest='count',
                        help='Returns occurrence counts for a predefined set of dimensions',
                        required=False,
                        action='store')
    '''                 Parameters:
                            taxonKey – [int] A GBIF occurrence identifier
                            basisOfRecord – [str] A GBIF occurrence identifier
                            country – [str] A GBIF occurrence identifier
                            isGeoreferenced – [bool] A GBIF occurrence identifier
                            datasetKey – [str] A GBIF occurrence identifier
                            publishingCountry – [str] A GBIF occurrence identifier
                            typeStatus – [str] A GBIF occurrence identifier
                            issue – [str] A GBIF occurrence identifier
                            year – [int] A GBIF occurrence identifier  '''

    parser.add_argument('-cf', '--count_basisofrecord',
                        dest='count_basisofrecord',
                        help='Lists occurrence counts by basis of record',
                        required=False,
                        action='store_true')
                        
    parser.add_argument('-cy', '--count_year',
                        nargs=1,
                        dest='count_year',
                        help='Lists occurrence counts by year',
                        required=False,
                        type=int,
                        action='store')
    '''                 Parameters:
                            year – [int] year range, e.g., 1990,2000. Does not support ranges like asterisk,2010  '''
    
    parser.add_argument('-cd', '--count_datasets',
                        nargs=2,
                        dest='count_datasets',
                        help='Lists occurrence counts for datasets that cover a given taxon or country',
                        required=False,
                        action='store')
    '''                 Parameters: 
                            taxonKey – [int] Taxon key
                            country – [str] A country, two letter code  '''
    
    parser.add_argument('-cs', '--count_schema',
                        dest='count_schema',
                        help='List the supported metrics by the service',
                        required=False,
                        action='store_true')
                        
                        
    parser.add_argument('-cc', '--count_country',
                        nargs=1,
                        dest='count_country',
                        help='Lists occurrence counts for all countries covered by the data published by the given country',
                        required=False,
                        action='store')
    '''                 Parameters:
                            publishingCountry – [str] A two letter country code
    '''
    
    parser.add_argument('-cp', '--count_publishingCountry',
                        nargs=1,
                        dest='count_publishingCountry',
                        help='Lists occurrence counts for all countries that publish data about the given country',
                        required=False,
                        action='store')
    '''                 Parameters:
                            country – [str] A country, two letter code  '''

    ### DOWNLOAD ###
    parser.add_argument('-d', '--download',
                        nargs='*',
                        dest='download',
                        help='Spin up a download request for GBIF occurrence data',
                        required=False,
                        action='append')
    parser.add_argument('--type',
                        nargs=1,
                        dest='type',
                        help='One of: equals, and, or, lessThan, lessThanOrEquals, greaterThan, greaterThanOrEquals, in, within, not, like',
                        required=False,
                        action='store')
                            
    return parser
    
def handle_error():
    formatted_lines = traceback.format_exc().splitlines()
    print
    print ' ' + formatted_lines[-1]
    print
    sys.exit(1)

def print_out(dic):
    j = json.dumps(dic)
    parsed_json = json.loads(j)
    print json.dumps(parsed_json, indent=2, sort_keys=True)     



if __name__ == '__main__':

    args = get_parser().parse_args()
    #print(args)

    ### download ###
    if args.download is not None:
        try:
            if len(args.download) == 1:
                result = occ.download(args.download[0])

            elif len(args.download) > 1:
                download_arg = []
                for item in args.download:
                    download_arg.append(item)

                if args.type is not None:
                    key  = 'type'
                    result = occ.download(download_arg, **{key: args.type[0]})
                else:
                    result = occ.download(download_arg)

            print_out(result)
        except:
            handle_error()


    ### search ###
    if args.search is not None:
        try:
            searh_arg = {}
            for item in args.search:
                searh_arg[item[0]] = item[1]
                
            result = occ.search(**searh_arg)
            print_out(result)
        except:
            handle_error()
    
    ### get ###
    if args.get is not None:
        try:
            key  = 'key'
            result = occ.get(**{key: args.get[0]})
            print_out(result)
        except:
            handle_error()
        
    if args.get_verbatim is not None:
        try:
            key  = 'key'
            result = occ.get(**{key: args.get_verbatim[0]})
            print_out(result)
        except:
            handle_error()
          
    if args.get_fragment is not None:
        try:
            key  = 'key'
            result = occ.get(**{key: args.get_fragment[0]})
            print_out(result)
        except:
            handle_error()
            
    ### counts ###
    if args.count is not None:
        try:
            result = occ.count(**{args.count[0]: args.count[1]})
            print_out(result)     
        except:
            handle_error()
            
    if args.count_basisofrecord is True:
        try:
            result = occ.count_basisofrecord()
            print_out(result)
        except:
            handle_error()
            
    if args.count_year is not None:
        try:
            year = 'year'
            result = occ.count_year(**{year: args.count_year[0]})
            print_out(result)     
        except:
            handle_error()
            
    if args.count_datasets is not None:
        try:
            result = occ.count_datasets(**{args.count_datasets[0]: args.count_datasets[1]})
            print_out(result)     
        except:
            handle_error()
            
    if args.count_schema is True:
        try:
            result = occ.count_schema()
            print_out(result)    
        except:
            handle_error()

    if args.count_country is not None:
        try:
            result = occ.count_countries(**{publishingCountry  : args.count_country[0]})
            print_out(result)
        except:
            handle_error()
            
    if args.count_publishingCountry is not None:
        try:
            result = occ.publishingCountry(**{country  : args.count_publishingCountry[0]})
            print_out(result)     
        except:
            handle_error()

    
    
    
