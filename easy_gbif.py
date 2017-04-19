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
from config import *
from pygbif import occurrences as occ
from pygbif import registry
from pygbif import species


def _check_environ(variable, value):
    """check if a variable is present in the environmental variables"""
    if value is not None and value:
        return value
    else:
        value = os.environ.get(variable)
        if value is None or not value:
            print "\n ",  variable, " not supplied and no entry in environmental variables"
            print "  You must first define GBIF_USER, GBIF_PWD and GBIF_EMAIL in env var\n"
            sys.exit(1)
        else:
            return value

def get_parser():

    """ Get parser object """
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='A program to manage gbif occurence module')

    if len(sys.argv[1:])==0:
        parser.print_help()
        # parser.print_usage() # for just the usage line
        parser.exit()

    parser.add_argument('-v', '--verbose',
                        help="show only parameters",
                        action="store_true")

    parser.add_argument('-json', '--json',
                        help="show output in formated json",
                        action="store_true")




    group_global_arg = parser.add_argument_group('group global arguments')
    group_global_arg.add_argument('--limit',
                        dest='limit',
                        help='limit  – [int] Controls the number of results in the page (Default: 300)',
                        required=False,
                        type=int,
                        default=300,
                        action='store')


    ### SEARCH #############################################
    group_search = parser.add_argument_group('group search')
    group_search.add_argument('-s', '--search',
                        dest='search',
                        help='Search GBIF occurrences',
                        required=False,
                        action='store_true')

    group_search_arg = parser.add_argument_group('group search arguments')
    group_search_arg.add_argument('--offset',
                        dest='offset',
                        help='offset  - [int] Determines the offset for the search results. A limit of 20 and offset of 20, will get the second page of 20 results.',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--q',
                        dest='q',
                        help='q  – [str] Simple search parameter. The value for this parameter can be a simple word or a phrase.',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sSpellCheck',
                        dest='sSpellCheck',
                        help='sSpellCheck  – [bool] If True ask GBIF to check your spelling of the value passed to the search parameter. IMPORTANT: This only checks the input to the search parameter, and no others. Default: False',
                        required=False,
                        action='store_true')

    group_search_arg.add_argument('--sRepatriated',
                        dest='sRepatriated',
                        help='sRepatriated  – [str] Searches for records whose publishing country is different to the country where the record was recorded in',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sTaxonKey',
                        dest='sTaxonKey',
                        help='sTaxonKey  – [int] A taxon key from the GBIF backbone',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sKingdomKey',
                        dest='sKingdomKey',
                        help='sKingdomKey  – [int] Kingdom classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sPhylumKey',
                        dest='sPhylumKey',
                        help='sPhylumKey  – [int] Phylum classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sClassKey',
                        dest='sClassKey',
                        help='sClassKey  – [int] Class classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sOrderKey',
                        dest='sOrderKey',
                        help='sOrderKey  – [int] Order classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sFamilyKey',
                        dest='sFamilyKey',
                        help='sFamilyKey  – [int] Family classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sGenusKey',
                        dest='sGenusKey',
                        help='sGenusKey  – [int] Genus classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sSubgenusKey',
                        dest='sSubgenusKey',
                        help='sSubgenusKey  – [int] Subgenus classification key',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sScientificName',
                        dest='sScientificName',
                        help='sScientificName  – [str] A scientific name from the GBIF backbone. All included and synonym taxa are included in the search',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sDatasetKey',
                        dest='sDatasetKey',
                        help='sDatasetKey  – [str] The occurrence dataset key (a uuid)',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sCatalogNumber',
                        dest='sCatalogNumber',
                        help='sCatalogNumber  – [str] An identifier of any form assigned by the source within a physical collection or digital dataset for the record which may not unique, but should be fairly unique in combination with the institution and collection code',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sRecordedBy',
                        dest='sRecordedBy',
                        help='sRecordedBy  – [str] The person who recorded the occurrence',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sCollectionCode',
                        dest='sCollectionCode',
                        help='sCollectionCode  – [str] An identifier of any form assigned by the source to identify the physical collection or digital dataset uniquely within the text of an institution',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sInstitutionCode',
                        dest='sInstitutionCode',
                        help='sInstitutionCode  – [str] An identifier of any form assigned by the source to identify the institution the record belongs to. Not guaranteed to be que',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sCountry',
                        dest='sCountry',
                        help='sCountry  –  [str] The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded',
                        required=False,
                        action='store')


    group_search_arg.add_argument('--sPublishingCountry',
                        dest='sPublishingCountry',
                        help='sPublishingCountry  – [str] The 2-letter country code (as per ISO-3166-1) of the owining organization\'s country',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sBasisOfRecord',
                        dest='sBasisOfRecord',
                        help='sBasisOfRecord – [str] Basis of record as defined in http://gbif.github.io/gbif-api/apidocs/org/gbif/api/vocabulary/BasisOfRecord.html',
                        choices=['FOSSIL_SPECIMEN', 'HUMAN_OBSERVATION', 'LITERATURE', 'LIVING_SPECIMEN', 'MACHINE_OBSERVATION', 'OBSERVATION', 'PRESERVED_SPECIMEN', 'UNKNOWN'],
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sEventDate',
                        dest='sEventDate',
                        help='sEventDate  – [date] Occurrence date in ISO 8601 format: yyyy, yyyy-MM, yyyy-MM-dd, or MM-dd. Supports range queries, smaller,larger (e.g., 1990,1991, whereas 1991,1990 wouldn’t work)',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sYear',
                        dest='sYear',
                        help='sYear  – [int] The 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sMonth',
                        dest='sMonth',
                        help='sMonth  – [int] The month of the year, starting with 1 for January. Supports range queries, smaller,larger (e.g., 1,2, whereas 2,1 wouldn’t work)',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sDecimalLatitude',
                        dest='sDecimalLatitude',
                        help='sDecimalLatitude  – [float] Latitude in decimals between -90 and 90 based on WGS 84. Supports range queries, smaller,larger (e.g., 25,30, whereas 30,25 wouldn’t work)',
                        required=False,
                        type=float,
                        action='store')

    group_search_arg.add_argument('--sDecimalLongitude',
                        dest='sDecimalLongitude',
                        help='sDecimalLongitude  – [float] Longitude in decimals between -180 and 180 based on WGS 84. Supports range queries (e.g., -0.4,-0.2, whereas -0.2,-0.4 wouldn’t work)',
                        required=False,
                        type=float,
                        action='store')

    group_search_arg.add_argument('--sElevation',
                        dest='sElevation',
                        help='sElevation  – [int/str] Elevation in meters above sea level. Supports range queries, smaller,larger (e.g., 5,30, whereas 30,5 wouldn’t work)',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sDepth',
                        dest='sDepth',
                        help='sDepth  – [int/str] Depth in meters relative to elevation. For example 10 meters below a lake surface with given elevation. Supports range queries, smaller,larger (e.g., 5,30, whereas 30,5 wouldn’t work)',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sGeometry',
                        dest='sGeometry',
                        help='sGeometry  – [str] Searches for occurrences inside a polygon described in Well Known Text (WKT) format. A WKT shape written as either POINT, LINESTRING, LINEARRING POLYGON, or MULTIPOLYGON. Example of a polygon: ((30.1 10.1, 20, 20 40, 40 40, 30.1 10.1)) would be queried as http://bit.ly/1BzNwDq',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sHasGeospatialIssue',
                        dest='sHasGeospatialIssue',
                        help='sHasGeospatialIssue  – [bool] Includes/excludes occurrence records which contain spatial issues (as determined in our record interpretation), i.e. hasGeospatialIssue=TRUE returns only those records with spatial issues while hasGeospatialIssue=FALSE includes only records without spatial issues. The absence of this parameter returns any record with or without spatial issues',
                        required=False,
                        action='store_true')

    group_search_arg.add_argument('--sIssue',
                        dest='sIssue',
                        help='sIssue  – [str] One or more of many possible issues with each occurrence record. See Details. Issues passed to this parameter filter results by the issue',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sHasCoordinate',
                        dest='sHasCoordinate',
                        help='sHasCoordinate  – [bool] Return only occurence records with lat/long data (true) or all records (false, default)',
                        required=False,
                        action='store_true')

    group_search_arg.add_argument('--sTypeStatus',
                        dest='sTypeStatus',
                        help='sTypeStatus  – [str/list] Type status of the specimen. One of many options',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sRecordNumber',
                        dest='sRecordNumber',
                        help='sRecordNumber  – [int] Number recorded by collector of the data, different from GBIF record number. See http://rs.tdwg.org/dwc/terms/#recordNumber}',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sLastInterpreted',
                        dest='sLastInterpreted',
                        help='sLastInterpreted  – [date] Date the record was last modified in GBIF, in ISO 8601 format: yyyy, yyyy-MM, yyyy-MM-dd, or MM-dd. Supports range queries, smaller,larger (e.g., 1990,1991, whereas 1991,1990 wouldn’t work)',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sContinent',
                        dest='sContinent',
                        help='sContinent  – [str] Continent',
                        choices=['africa', 'antarctica', 'asia', 'europe', 'north_america', 'south_america', 'oceania'],
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sFields',
                        dest='sFields',
                        help='sFields  – [str] Default (all) returns all fields. minimal returns just taxon name, key, latitude, and longitude. Or specify each field you want returned by name, e.g. fields = c(\'name\',\'latitude\',\'elevation\')',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sMediatype',
                        dest='sMediatype',
                        help='sMediatype  – [str] Media type',
                        choices=['NULL', 'MovingImage', 'Sound', 'StillImage'],
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sFacet',
                        dest='sFacet',
                        help='sFacet  – [str] a character vector of length 1 or greater',
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sEstablishmentMeans',
                        dest='sEstablishmentMeans',
                        help='sEstablishmentMeans  – [str] EstablishmentMeans',
                        choices=['INTRODUCED', 'INVASIVE', 'MANAGED', 'NATIVE', 'NATURALISED', 'UNCERTAIN'],
                        required=False,
                        action='store')

    group_search_arg.add_argument('--sFacetMincount',
                        dest='sFacetMincount',
                        help='sFacetMincount  – [int] minimum number of records to be included in the faceting results',
                        required=False,
                        type=int,
                        action='store')

    group_search_arg.add_argument('--sFacetMultiselect',
                        dest='sFacetMultiselect',
                        help='sFacetMultiselect  – [bool] Set to true to still return counts for values that are not currently filtered. See examples. Default: false',
                        required=False,
                        action='store_true')



    ### GET #########################################
    group_get = parser.add_argument_group('group get')
    group_get.add_argument('-g', '--get',
                            dest='get',
                            help='Gets details for a single, interpreted occurrence. Must specify --gKey',
                            required=False,
                            action='store_true')

    group_get.add_argument('-gv', '--get_verbatim',
                            dest='get_verbatim',
                            help='Gets a verbatim occurrence record without any interpretation. Must specify --gKey',
                            required=False,
                            action='store_true')

    group_get.add_argument('-gf', '--get_fragment',
                            dest='get_fragment',
                            help='Get a single occurrence fragment in its raw form (xml or json). Must specify --gKey',
                            required=False,
                            action='store_true')


    group_get_arg = parser.add_argument_group('group get arguments')
    group_get_arg.add_argument('--gKey',
                        dest='gKey',
                        help='gKey  – [int] A GBIF occurrence key',
                        required=False,
                        type=int,
                        action='store')



    ### COUNT ##########################################################
    group_count = parser.add_argument_group('group count')
    group_count.add_argument('-c', '--count',
                        dest='count',
                        help='Returns occurrence counts for a predefined set of dimensions. Must specify one or more of: --cTaxonKey, --cBasisOfRecord, --cCountry, --cIsGeoreferenced, --cDatasetKey, --cPublishingCountry, --cTypeStatus, --cIssue, --cYear',
                        required=False,
                        action='store_true')

    group_count.add_argument('-cf', '--count_basisofrecord',
                        dest='count_basisofrecord',
                        help='Lists occurrence counts by basis of record',
                        required=False,
                        action='store_true')

    group_count.add_argument('-cy', '--count_year',
                        dest='count_year',
                        help='Lists occurrence counts by year. Must specify --cYear',
                        required=False,
                        action='store_true')

    group_count.add_argument('-cd', '--count_datasets',
                        dest='count_datasets',
                        help='Lists occurrence counts for datasets that cover a given taxon or country. Must specify one or more of: --cTaxonKey, --cCountry',
                        required=False,
                        action='store_true')

    group_count.add_argument('-cc', '--count_country',
                        dest='count_country',
                        help='Lists occurrence counts for all countries covered by the data published by the given country. Must specify --cPublishingCountry',
                        required=False,
                        action='store_true')

    group_count.add_argument('-cs', '--count_schema',
                        dest='count_schema',
                        help='List the supported metrics by the service',
                        required=False,
                        action='store_true')

    group_count.add_argument('-cp', '--count_publishingCountry',
                        dest='count_publishingCountry',
                        help='Lists occurrence counts for all countries that publish data about the given country. Must specify --cCountry',
                        required=False,
                        action='store_true')

    group_count_arg = parser.add_argument_group('group count arguments')

    group_count_arg.add_argument('--cKey',
                        dest='cKey',
                        help='cKey  – [int] A GBIF occurrence key',
                        required=False,
                        type=int,
                        action='store')

    group_count_arg.add_argument('--cBasisOfRecord',
                        dest='cBasisOfRecord',
                        help='cBasisOfRecord – [str] Basis of record as defined in http://gbif.github.io/gbif-api/apidocs/org/gbif/api/vocabulary/BasisOfRecord.html',
                        choices=['FOSSIL_SPECIMEN', 'HUMAN_OBSERVATION', 'LITERATURE', 'LIVING_SPECIMEN', 'MACHINE_OBSERVATION', 'OBSERVATION', 'PRESERVED_SPECIMEN', 'UNKNOWN'],
                        required=False,
                        action='store')

    group_count_arg.add_argument('--cCountry',
                        dest='cCountry',
                        help='cCountry  – [str] A country, two letter code',
                        required=False,
                        action='store')

    group_count_arg.add_argument('--cIsGeoreferenced',
                        dest='cIsGeoreferenced',
                        help='cIsGeoreferenced – [bool]',
                        required=False,
                        action='store_true')


    group_count_arg.add_argument('--cDatasetKey',
                        dest='cDatasetKey',
                        help='cDatasetKey  – [str] The occurrence dataset key (a uuid).',
                        required=False,
                        action='store')


    group_count_arg.add_argument('--cPublishingCountry',
                        dest='cPublishingCountry',
                        help='cPublishingCountry  – [str] The 2-letter country code (as per ISO-3166-1) of the country in which the occurrence was recorded.',
                        required=False,
                        action='store')


    group_count_arg.add_argument('--cTypeStatus',
                        dest='cTypeStatus',
                        help='cTypeStatus  – [str] Nomenclatural type (type status, typified scientific name, publication) applied to the subject',
                        required=False,
                        action='store')

    group_count_arg.add_argument('--cIssue',
                        dest='cIssue',
                        help='cIssue  – [str/list] One or more of many possible issues with each occurrence record. See Details. Issues passed to this parameter filter results by the issue',
                        required=False,
                        action='store')

    group_count_arg.add_argument('--cYear',
                        dest='cYear',
                        help='cYear  – [int] The 4 digit year. A year of 98 will be interpreted as AD 98. Supports range queries',
                        required=False,
                        action='store')

    group_count_arg.add_argument('--cTaxonKey',
                        dest='cTaxonKey',
                        help='cTaxonKey  – [int] Taxon key',
                        required=False,
                        type=int,
                        action='store')


    ### DOWNLOAD ###############################################################
    group_download = parser.add_argument_group('group download')
    group_download.add_argument('-d', '--download',
                        dest='download',
                        help='Spin up a download request for GBIF occurrence data. Must specify --queries and --query_type',
                        required=False,
                        action='store_true')

    group_download.add_argument('-dm', '--download_meta',
                        dest='download_meta',
                        help='Retrieves the occurrence download metadata by its unique key. Must specify --dKey',
                        required=False,
                        action='store_true')

    group_download.add_argument('-dl', '--download_list',
                        dest='download_list',
                        help='Lists the downloads created by a user',
                        required=False,
                        action='store_true')

    group_download.add_argument('-dg', '--download_get',
                        dest='download_get',
                        help='Get a download from GBIF. Must specify --dKey [--path]',
                        required=False,
                        action='store_true')

    group_download_arg = parser.add_argument_group('group download arguments')
    group_download_arg.add_argument('--dKey',
                        dest='dKey',
                        help='dKey -  [str] A key generated from a request, like that from download',
                        required=False,
                        action='store')

    group_download_arg.add_argument('-q', '--queries',
                        nargs='+',
                        dest='queries',
                        help='One or more of query arguments to kick of a download job. Argument passed have to be passed as character (e.g., country = US), with a space between key, operator  and value. See the type parameter for possible options for the operator.',
                        required=False,
                        action='append')

    group_download_arg.add_argument('--q_type',
                        dest='q_type',
                        help='One of: equals, and, or, lessThan, lessThanOrEquals, greaterThan, greaterThanOrEquals, in, within, not, like. Used with --download',
                        required=False,
                        default = 'and',
                        action='store')

    group_download_arg.add_argument('--path',
                        dest='path',
                        help='Path to write zip file to. Default: ".", with a .zip appended to the end. Used with --download_get',
                        required=False,
                        action='store')


    return parser.parse_args()

def handle_error():
    formatted_lines = traceback.format_exc().splitlines()
    print
    print ' ' + formatted_lines[-1]
    print
    sys.exit(1)

def print_out(dic):
    if args.json is True:
        print json.dumps(dic, indent=2, sort_keys=False)
    else:
        print json.dumps(dic)


if __name__ == '__main__':

    user  = _check_environ('GBIF_USER', user)
    pwd   = _check_environ('GBIF_PWD', pwd)
    email = _check_environ('GBIF_EMAIL', email)

    args = get_parser()

    if args.verbose is True:
        print args
        print
        for arg in vars(args):
            if getattr(args, arg) is not None and getattr(args, arg) is not False:
                print arg, getattr(args, arg)
        print

        sys.exit(1)

    ###########################################################################################
    ### download ##############################################################################
    if args.download is True:
        try:
            if args.queries is not None:
                result = occ.download(args.queries[0], pred_type=args.q_type)
                print_out(result)
            else:
                print " queries arguments are required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.download_meta is True:
        try:
            if args.dKey is not None:
                result = occ.download_meta(key=args.dKey)
                print_out(result)
            else:
                print " --dKey argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.download_list is True:
        try:
            result = occ.download_list(user=user, pwd=pwd, limit=20, offset=0)
            print_out(result)
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.download_get is True:
        try:
            if args.dKey is not None:
                result = occ.download_get(key=args.dKey, path=args.path)
                print_out(result)
            else:
                print " --dKey argument is required [--path]"
        except:
            handle_error()
        finally:
           sys.exit(0)


    ### SEARCH ##############################################################################
    if args.search is True:
        try:
            if args.sTaxonKey is not None or args.sRepatriated is not None or args.sKingdomKey is not None or \
               args.sPhylumKey is not None or args.sClassKey is not None or args.sOrderKey is not None or \
               args.sFamilyKey is not None or args.sGenusKey is not None or args.sSubgenusKey is not None or \
               args.sScientificName is not None or args.sCountry is not None or args.sPublishingCountry is not None or \
               args.sHhasCoordinate is True or args.sTypeStatus is not None or args.sRecordNumber is not None or \
               args.sLastInterpreted is not None or args.sContinent is not None or args.sGeometry is not None or \
               args.sRecordedBy is not None or args.sBasisOfRecord is not None or args.sYear is not None or \
               args.sMonth is not None or args.sDecimalLatitude is not None or args.sDecimalLongitude is not None or \
               args.sElevation is not None or args.sDepth is not None or args.sInstitutionCode is not None or \
               args.sCollectionCode is not None or args.sHasGeospatialIssue is True or args.sIssue is not None or \
               args.q is not None or args.sSpellCheck is True or args.sMediatype is not None or \
               args.sEstablishmentMeans is not None or args.sFacet is not None or \
               args.sFacetMincount is not None or args.sFacetMultiselect is True:

                result = occ.search(taxonKey=args.sTaxonKey, repatriated=args.sRepatriated, kingdomKey=args.sKingdomKey,
                                    phylumKey=args.sPhylumKey, classKey=args.sClassKey, orderKey=args.sOrderKey,
                                    familyKey=args.sFamilyKey, genusKey=args.sGenusKey, subgenusKey=args.sSubgenusKey,
                                    scientificName=args.sScientificName, country=args.sCountry,
                                    publishingCountry=args.sPublishingCountry, hasCoordinate=args.sHasCoordinate,
                                    typeStatus=args.sTypeStatus, recordNumber=args.sRecordNumber,
                                    lastInterpreted=args.sLastInterpreted, continent=args.sContinent,
                                    geometry=args.sGeometry, recordedBy=args.sRecordedBy, basisOfRecord=args.sBasisOfRecord,
                                    datasetKey=args.sDatasetKey, eventDate=args.sEventDate, catalogNumber=args.sCatalogNumber,
                                    year=args.sYear, month=args.sMonth, decimalLatitude=args.sDecimalLatitude,
                                    decimalLongitude=args.sDecimalLongitude, elevation=args.sElevation, depth=args.sDepth,
                                    institutionCode=args.sInstitutionCode, collectionCode=args.sCollectionCode,
                                    hasGeospatialIssue=args.sHasGeospatialIssue, issue=args.sIssue, q=args.q,
                                    spellCheck=args.sSpellCheck, mediatype=args.sMediatype,
                                    establishmentMeans=args.sEstablishmentMeans, facet=args.sFacet,
                                    facetMincount=args.sFacetMincount, facetMultiselect=args.sFacetMultiselect,
                                    limit=args.limit, offset=args.offset)
                print_out(result)
            else:
                print " More arguments are required"
        except:
            handle_error()
        finally:
           sys.exit(0)



    ### GET ##############################################################################
    if args.get is True:
        try:
            if args.gKey is not None:
                result = occ.get(key=args.gKey)
                print_out(result)
            else:
                print " --gKey argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.get_verbatim is True:
        try:
            if args.gKey is not None:
                result = occ.get_verbatim(key=args.gKey)
                print_out(result)
            else:
                print " --gKey argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.get_fragment is True:
        try:
            if args.gKey is not None:
                result = occ.get_fragment(key=args.gKey)
                print_out(result)
            else:
                print " --gKey argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)


    ### COUNT ##############################################################################
    if args.count is True:
        try:
            if args.cTaxonKey is not None or args.cBasisOfRecord is not None or args.cCountry is not None or \
               args.cIsGeoreferenced is True or args.cDatasetKey is not None or \
               args.cPublishingCountry is not None or args.cTypeStatus is not None or \
               args.cIssue is not None or args.cYear is not None :

                result = occ.get_fragment(taxonKey=args.cTaxonKey, basisOfRecord=args.cBasisOfRecord,
                                          country=args.cCountry, cIsGeoreferenced=args.cIsGeoreferenced,
                                          datasetKey=args.cDatasetKey, publishingCountry=args.cPublishingCountry,
                                          typeStatus=args.cTypeStatus, issue=args.cIssue, year=args.cYear)
                print_out(result)
            else:
                print " More arguments are required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.count_basisofrecord is True:
        try:
            result = occ.count_basisofrecord()
            print_out(result)
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.count_year is True:
        try:
            if args.cYear is not None:
                result = occ.count_year(year=args.cYear)
                print_out(result)
            else:
                print " --cYear argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)
            
    if args.count_datasets is True:
        try:
            if args.cCountry is not None or args.cTaxonKey is not None:
                result = occ.count_datasets(taxonKey=args.cTaxonKey, country=args.cCountry)
                print_out(result)
            else:
                print " --cTaxonKey and/or --cCountry argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.count_country is True:
        try:
            if args.cPublishingCountry is not None:
                result = occ.count_countries(publishingCountry=args.cPublishingCountry)
                print_out(result)
            else:
                print " --cPublishingCountry argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.count_schema is True:
        try:
            result = occ.count_schema()
            print_out(result)
        except:
            handle_error()
        finally:
           sys.exit(0)

    if args.count_publishingCountry is True:
        try:
            if args.cCountry is not None:
                result = occ.publishingCountry(country=args.cCountry)
                print_out(result)
            else:
                print " --cCountry argument is required"
        except:
            handle_error()
        finally:
           sys.exit(0)
