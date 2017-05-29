#!/usr/bin/perl

use strict;
use Getopt::Long;
use Geo::Hash;
use Geo::Hash::XS;
use Geo::Hash::Grid;
use Bio::Community;
use Bio::Community::Member;
use Bio::Community::Meta;
use Bio::Community::Tools::Accumulator;
use Data::Dumper;

$| = 1;

my ($file_input, $file_output, $help, $verbose, $mverbose, $ini_year,$end_year);

######## options/help ########
GetOptions(
    'help|h'                    => \$help,
    'verbose|v'                 => \$verbose,
    'mverbose|vv'               => \$mverbose,
    'input|i=s'                 => \$file_input,
    'output|o=s'                => \$file_output,
    'iniyear|iy=i'              => \$ini_year,
    'endyear|ey=i'              => \$end_year,
) or die "\n Invalid commmand line options.\n";

my $USAGE =<<USAGE;
    Usage:
         $0 [-h|--help]
            [-v|--verbose]
            [-vv|--mverbose]
            [-i|--input]
            [-o|--output]
            [-iy|--iniyear]
            [-ey|--endyear]
            

    Options:
          -h,  --help          show this help
          -v,  --verbose       verbose mode
          -vv, --mverbose       more verbose mode
          -i,  --input         input file
          -o,  --output        output file
          -iy, --iniyear       start year
          -ey, --endyear       end year
         
USAGE

## check arguments
if($help) {
    print "$USAGE\n";
    exit 1;
}
if(!$file_input){
    print "  $0: Argument required. \n";
    print "$USAGE\n";
    exit 1
}
if(!$ini_year){
    $ini_year = 0;
}
if(!$end_year){
    $end_year = 9999;
}

##
# Open the file for read access:
open INPUT, '<', $file_input;
open OUTPUT, '+>', 'localization.dat';
print OUTPUT "latitude;longitude;species\n";

# Set the character which will be used to indicate the end of a line.
local $/ = "\n";

###################################
print "== Creating grid\n";
## Cell dimensions vary with latitude 
## Length  Cell width  Cell height
##  1     ≤ 5000km     ×    5000km
##  2     ≤ 1250km     ×    625km
##  3     ≤ 156km      ×    156km
##  4     ≤ 39.1km     ×    19.5km
##  5     ≤ 4.89km     ×    4.89km
##  6     ≤ 1.22km     ×    0.61km
##  7     ≤ 153m       ×    153m
##  8     ≤ 38.2m      ×    19.1m
##  9     ≤ 4.77m      ×    4.77m
##  10    ≤ 1.19m      ×    0.596m
##  11    ≤ 149mm      ×    149mm
##  12    ≤ 37.2mm     ×    18.6mm


my $precision = 5;
my $south_west_latitude  = 36.8;
my $south_west_longidude = -9.7;
my $north_east_latitude  = 42.1;
my $north_east_longitude = -6.2;


my $grid = Geo::Hash::Grid->new(
        sw_lat    => $south_west_latitude,
        sw_lon    => $south_west_longidude,
        ne_lat    => $north_east_latitude,
        ne_lon    => $north_east_longitude,
        precision => $precision,
    );
my $hash_count        = $grid->count;
my $geohash_array_ref = $grid->hashes;


my %big_data = ();
foreach my $geohash (@$geohash_array_ref) {
    $big_data{$geohash}{'sum'} = 0;
    $big_data{$geohash}{'species'} = ();
}

###################################
my @parse_line = ();
my ($ncol_gbifid, $ncol_lat, $ncol_lon, $ncol_species, $ncol_year);

my $lat_min=99;
my $lat_max=-99;
my $lon_min=999;
my $lon_max=-999;

# Loop through each line:
print "== Reading input file\n";
my $ncols;
while (my $row = <INPUT>){    
    next if ($row =~ /^\s*$/);
    
    if($row =~ /^\w+\s+\w+\s+\w+/){
        #print $row ."\n";
        ## first line
        @parse_line = split /\t/, $row;
        my $ncol = 0;
        foreach my $col (@parse_line){
            if($col =~ /gbifid/){
                $ncol_gbifid = $ncol;
                #print "gbifid: $ncol_gbifid \n";
            }elsif($col =~ /lat/){
                $ncol_lat = $ncol;
                #print "latitude: $ncol_lat \n";
            }elsif($col =~ /lon/){
                $ncol_lon = $ncol;
                #print "longitude: $ncol_lon \n";
            }elsif($col =~ /taxonkey/){
                $ncol_species = $ncol;
                #print "species: $ncol_species \n";
            }elsif($col =~ /year/){
                $ncol_year = $ncol;
                #print "year: $ncol_year \n";
            }
            $ncol ++;
        }
        $ncols = $#parse_line;
    }else{
        @parse_line = split /\t/, $row;
        if($#parse_line != $ncols){
            print " line don\'t match. Expected: $ncols. $#parse_line  \n";
            print $row ."\n";
            exit;
        }
        
        my $gbifid  = $parse_line[$ncol_gbifid];
        my $lat     = $parse_line[$ncol_lat];
        my $lon     = $parse_line[$ncol_lon];
        my $species = $parse_line[$ncol_species];
        my $year    = $parse_line[$ncol_year];
        
        if($lon > -10 and $lon < -6 and $lat > 36 and $lat < 43 and $year >= $ini_year and $year <= $end_year){
            ## min max latitude
            $lat_min = $lat if($lat < $lat_min);
            $lat_max = $lat if($lat > $lat_max);
        
            ## min max longitude
            $lon_min = $lon if($lon < $lon_min);
            $lon_max = $lon if($lon > $lon_max);
            
            print OUTPUT "$lat;$lon;$species\n";
            
            ## verify if species id exist
            if($species !~ /\d+/){
                print "$gbifid,  $lat,  $lon,  $species\n";
                my $i = 0;
                foreach (@parse_line){
                    print "$i      $_\n";
                    $i++;
                }
                exit;
            }
            
            my $gh = Geo::Hash::XS->new();
            my $geohash = $gh->encode($lat, $lon, $precision);
            if(exists $big_data{$geohash}){
                $big_data{$geohash}{'sum'} = $big_data{$geohash}{'sum'} + 1;
                $big_data{$geohash}{'species'}{$species}{'id'} = $species;
                if(exists $big_data{$geohash}{'species'}{$species}){
                    $big_data{$geohash}{'species'}{$species}{'count'} = $big_data{$geohash}{'species'}{$species}{'count'} + 1;
                }else{
                    $big_data{$geohash}{'species'}{$species}{'count'} = 1;
                }
            }else{
                print " New geohash: $geohash \n";
                exit;
            }
        }
    }
}

if($mverbose){
    print " lat range: $lat_min  $lat_max      lon range: $lon_min  $lon_max  \n";

    my $south_west_latitude = sprintf "%.1f", $lat_min - 0.1;
    my $south_west_longidude = sprintf "%.1f", $lon_min + 0.1;
    my $north_east_latitude = sprintf "%.1f", $lat_max + 0.1;
    my $north_east_longitude = sprintf "%.1f", $lon_max + 0.1;

    print "\n";
    print "($south_west_longidude,$north_east_latitude) |----------------------| ($north_east_longitude,$north_east_latitude)\n";
    print "            |                      |\n"; 
    print "            |                      |\n";
    print "            |                      |\n";
    print "            |                      |\n";
    print "            |                      |\n";
    print "            |                      |\n";
    print "($south_west_longidude,$south_west_latitude) |----------------------| ($north_east_longitude,$south_west_latitude)\n";
    print "\n";
}

close INPUT;
close OUTPUT;

#print Dumper(\%big_data);
#exit;


print "== statistics\n";

my $size_geo = keys %big_data;

open OUTPUT, '+>', $file_output;

open OUTGEO, '+>', "geohash.dat";

my @community_list = ();
my $community_accepted = 0;
foreach my $geohash (sort keys %big_data){
    
    ## filter geohash localization
    my $gh = Geo::Hash->new;
    my ( $lat, $lon ) = $gh->decode( $geohash );
    if($lat > 39.7 or $lat < 37.3 ){
        print "skip  $geohash ($lat, $lon)\n" if($verbose);
        next;
    }
    
    print "  = Community $geohash ($lat, $lon)\n" if($verbose);
    my $community = Bio::Community->new( -name => $geohash );

    my @community_member_list = ();

    ## Add members to community
    while (my ($specie_key, $specie_val) = each %{ $big_data{$geohash}{'species'} } ){
        my $member = Bio::Community::Member->new( -id => $big_data{$geohash}{'species'}{$specie_key}{'id'} );
        my $member_count = $big_data{$geohash}{'species'}{$specie_key}{'count'};
        $community->add_member( $member, $member_count );
        
        for( my $i=1; $i <= $member_count; $i++ ){
            push @community_member_list,  $member->id();
        }
    }
    push @community_list, $community;
    

    my $members_count = $community->get_members_count;
    my $richness = $community->get_richness;
    print "   There are $members_count members in the community\n" if($verbose);
    print "   The total diversity is $richness species\n" if($verbose);

    if($mverbose){
        while (my $member = $community->next_member) {
            my $member_id     = $member->id;
            my $member_count  = $community->get_count($member);
            my $member_rel_ab = $community->get_rel_ab($member);
            my $member_rank = $community->get_rank($member);
            print "     The relative abundance of member $member_id is $member_rel_ab % ($member_count counts). Rank is $member_rank\n";
        }
    }
    
    my $members = $community->get_all_members();
    #print Dumper($members);
   
    ## print header
    if($members_count > 2){
        $community_accepted++;
        print OUTGEO "$lat;$lon;$geohash;1\n";
        print OUTPUT "Cell $geohash ($lat, $lon)\t*SampleSet*\t1\t1\t1\n";
        print OUTPUT "$richness\t$members_count\n";
        for( my $i=1; $i<=$members_count; $i++ ){
            my $sample_id = sprintf("%05d", $i);
            print OUTPUT "\t$sample_id";
        }
        print OUTPUT "\n";

        ## set matrix
        my %matrix = (); ## matrix data for random get
        for( my $i=1; $i<=$members_count; $i++ ){
            ## get random member
            my $rand_index = 0 + int(rand($#community_member_list - 0));
            my $rand_member = $community_member_list[$rand_index];
    
            ## remove getted member from community
            splice @community_member_list, $rand_index, 1;
            print "$geohash   $members_count  ".@community_member_list."  --> $rand_index (0 - ".@community_member_list.") --> $rand_member\n" if($verbose);
    
            while (my $member = $community->next_member) {
                my $member_id     = $member->id;
                if($member_id eq $rand_member){
                    push( @{ $matrix{$member_id} }, 1); 
                }else{
                    push( @{ $matrix{$member_id} }, 0); 
                }
            }
        }

        ## print matrix
        foreach my $member_id (sort {lc $a cmp lc $b} keys %matrix) {
            print OUTPUT "$member_id";
            for( my $i=0; $i<$members_count; $i++ ){
                print OUTPUT "\t".$matrix{$member_id}[$i];
            }
            print OUTPUT "\n";
        }

        #last if($community_accepted == 100);
    }else{
        print OUTGEO "$lat;$lon;$geohash;0\n";
    }
    
}
close OUTPUT;
close OUTGEO;

open INPUT,  '<',  $file_output      or die "Can't read old file: $!";
open OUTPUT, '>', "$file_output.new" or die "Can't write new file: $!";
print OUTPUT "*MultipleSampleSets*\t$community_accepted\tPT Community with more then 2 members";
if($ini_year != 0){
    print OUTPUT "; start year: $ini_year";
}
if($end_year != 9999){
    print OUTPUT ", end year: $end_year";
}
print OUTPUT "\n";

while( <INPUT> ){
        print OUTPUT $_;
}
close OUTPUT;

unlink $file_output;
rename "$file_output.new", $file_output;


## Meta Community
my $meta = Bio::Community::Meta->new( -name => 'PT' );
$meta->add_communities( \@community_list );
print "\n== Metacommunity contains:\n";
print "   ".$meta->get_communities_count." communities\n";
print "   ".$meta->get_richness." species\n";
print "   ".$meta->get_members_count." individuals\n";

print "   $community_accepted with more then 2 members\n";









