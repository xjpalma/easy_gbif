#!/usr/bin/perl

use strict;
use Getopt::Long;
use Cwd;
use JSON;
use DateTime;
use Data::Dumper;

my $dir_download = 'download';

my ($d_args, $json_txt);
my ($run_d, $run_dl, $run_dm, $run_dg, $key, $help);

######## options/help ########
GetOptions(
    'help|h'                    => \$help,
    'runDownload|d'             => \$run_d,
    'listDownload|dl'           => \$run_dl,
    'metaDownload|dm'           => \$run_dm,
    'getDownload|dg'            => \$run_dg,
    'key|k=s'                   => \$key,
) or die "\n Invalid commmand line options.\n";

my $USAGE =<<USAGE;

    Easy GBIF System Management.

    Usage:
         $0 [-h|--help]
                    [-d|--runDownload]
                   [-dl|--listDownload]
                   [-dm|--metaDownload [-k|--key <KEY>]]
                   [-dg|--getDownload  [-k|--key <KEY>]]

    Options:
          -h,  --help             show this help
          -d,  --runDownload      spin up a download request for GBIF occurrence data
         -dl,  --listDownload     lists the downloads created by a user
         -dm,  --metaDownload     retrieves the occurrence download metadata by its unique key
         -dg,  --getDownload      get a download from GBIF
          -k,  --key              a gbif key generated from a request
         
USAGE

## check arguments
if($help) {
    print "$USAGE\n";
    exit 1;
}

if (!$help and !$run_d and !$run_dl and !$run_dm and !$run_dg) {
    print "  $0: Argument required. \n";
    print "$USAGE\n";
    exit 1
}

if($run_dm){
    if($key !~ /\d+-\d/){
        print " key has bad format. key is: $key \n";
        exit 1;
    }
}

## ask download and when SUCCEEDED, download it
if($run_d){
    print " Enter a query arguments.\n Must be at format <'key1 op1 value1' 'key2 op2 value2' 'key3 op3 value3' ... >\n";
    my $d_args = <STDIN>;
    chomp $d_args;
    exit 0 if ($d_args eq ""); # If empty string, exit.


    #$d_args = "'basisOfRecord = HUMAN_OBSERVATION' 'country = PT' 'year = 1980,2017' 'month = 3,6' 'hasCoordinate = TRUE' 'hasGeospatialIssue = FALSE' 'taxonKey = 729'";
    
    my $json_txt = `python easy_gbif.py -d -q  $d_args`;
    
    my @output_d = split(/\n/, $json_txt);
    
    if($output_d[1] =~ /^\[.+\]$/){
        my @decoded_json = @{decode_json($output_d[1] )};
        
        my $d_key = $decoded_json[0];
        print " download key: $d_key \n";
                
        #### get download ####
        my $nTry = 1;
        my $sucess;
        do {
            $sucess = 0;
            if($d_key =~ /\d+-\d+/){
                $json_txt = `python easy_gbif.py -dm --dKey $d_key`;
                my $decoded_json = decode_json($json_txt);
                print " The download status is:  ".$decoded_json->{"status"} ."\n";
                if($decoded_json->{"status"} eq 'SUCCEEDED'){
                    ## download zip file
                    `mkdir -p download` ;
                    $json_txt = `python easy_gbif.py -dg --dKey $d_key --path $dir_download `;
                    
                    my @output_dg = split(/\n/, $json_txt);
                    if($output_dg[0] =~/Download file size/ and $output_dg[1] =~/On disk at/){
                        $sucess = 1;
                        print " $output_dg[0] \n";
                        print " $output_dg[1] \n";
                        #print " $output_dg[2] \n";
                    }
                }
            }
            ## wait 10 min
            if(!$sucess){
                print " $nTry - I will sleep 2 min and wait for SUCCEEDED status... \n";
                sleep 120
            }
            $nTry ++;
        }while($sucess == 0 and $nTry < 10);
        if($sucess == 0){
            print " Download NOT SUCCEEDED :( \n";
        }
    }else{
        print "\n Error: Don\'t know parse json output. Output is:  \n";
        print $output_d[1] ."\n";
    }
}

## download list
if($run_dl){
    my $json_txt = `python easy_gbif.py -dl -json`;
    print $json_txt ."\n";
}

## download metadata
if($run_dm){
    my $json_txt = `python easy_gbif.py -dm --dKey $key -json`;
    print $json_txt ."\n";
}

## download metadata
if($run_dg){
    $json_txt = `python easy_gbif.py -dm --dKey $key `;
    
    my $decoded_json = decode_json($json_txt);
    print " The download status is:  ".$decoded_json->{"status"} ."\n";
    if($decoded_json->{"status"} eq 'SUCCEEDED'){
        ## download zip file
        `mkdir -p download` ;
        $json_txt = `python easy_gbif.py -dg --dKey $key --path $dir_download `;
        
        my @output_dg = split(/\n/, $json_txt);
        if($output_dg[0] =~/Download file size/ and $output_dg[1] =~/On disk at/){
            print " $output_dg[0] \n";
            print " $output_dg[1] \n";
            #print " $output_dg[2] \n";
        }
    }else{
        print " Download NOT SUCCEEDED :( \n";
        exit 0;
    }
}
