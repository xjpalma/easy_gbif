#!/usr/bin/perl

use strict;
use Getopt::Long;
use Geo::Hash::XS;
use Geo::Hash::Grid;
use Bio::Community;
use Bio::Community::Member;
use Bio::Community::Meta;
use Bio::Community::Tools::Accumulator;
use Data::Dumper;



my ($file_input, $file_output, $help);

######## options/help ########
GetOptions(
    'help|h'                    => \$help,
    'input|i=s'                 => \$file_input,
    'output|o=s'                => \$file_output,
) or die "\n Invalid commmand line options.\n";

my $USAGE =<<USAGE;
    Usage:
         $0 [-h|--help]
            [-i|--input]
            [-o|--output]

    Options:
          -h,  --help          show this help
          -i,  --input         input file
          -o,  --output        output file
         
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
if(!$file_output){
    $file_output = 'output.dat';
}


##
# Open the file for read access:
open INPUT, '<', $file_input;
open OUTPUT, '+>', $file_output;
print OUTPUT "latitude;longitude;species\n";

# Set the character which will be used to indicate the end of a line.
local $/ = "\n";

###################################
print "== Creating grid\n";

#Length  Cell width  Cell height
# 1     ≤ 5,000km    ×    5,000km
# 2     ≤ 1,250km    ×    625km
# 3     ≤ 156km      ×    156km
# 4     ≤ 39.1km     ×    19.5km
# 5     ≤ 4.89km     ×    4.89km
# 6     ≤ 1.22km     ×    0.61km
# 7     ≤ 153m       ×    153m
# 8     ≤ 38.2m      ×    19.1m
# 9     ≤ 4.77m      ×    4.77m
# 10    ≤ 1.19m      ×    0.596m
# 11    ≤ 149mm      ×    149mm
# 12    ≤ 37.2mm     ×    18.6mm

my $precision = 3;
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
my ($ncol_gbifid, $ncol_lat, $ncol_lon, $ncol_species);

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
        
        if($lon > -10 and $lon < -6 and $lat > 36 and $lat < 43){
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

close INPUT;
close OUTPUT;

print Dumper(\%big_data);



my @community_array = ();
foreach my $geohash (sort keys %big_data){
    print "\n== Community $geohash \n";
    
    my $community = Bio::Community->new( -name => $geohash );
    
    ## Add members to community
    while (my ($specie_key, $specie_val) = each %{ $big_data{$geohash}{'species'} } ){
        my $member = Bio::Community::Member->new( -id => $big_data{$geohash}{'species'}{$specie_key}{'id'} );
        $community->add_member( $member, $big_data{$geohash}{'species'}{$specie_key}{'count'} );
    }
    
    print "   There are ".$community->get_members_count." members in the community\n";
    print "   The total diversity is ".$community->get_richness." species\n";
    while (my $member = $community->next_member) {
        my $member_id     = $member->id;
        my $member_count  = $community->get_count($member);
        my $member_rel_ab = $community->get_rel_ab($member);
        print "     The relative abundance of member $member_id is $member_rel_ab % ($member_count counts)\n";
    }

    push @community_array, $community;
    
}

## Meta Community
my $meta = Bio::Community::Meta->new( -name => 'PT' );
$meta->add_communities( \@community_array );
print "\n== Metacommunity contains:\n";
print "   ".$meta->get_communities_count." communities\n";
print "   ".$meta->get_richness." species\n";
print "   ".$meta->get_members_count." individuals\n";
print "   ".$meta->get_members_count." individuals\n";


## A collector curve
## In a collector curve, an increasing number of communities is randomly drawn and combined and their cumulative alpha diversity is determined.
print "\n== Collector curve\n";
if(1){
    my $collector = Bio::Community::Tools::Accumulator->new(
            -metacommunity   => $meta,
            -type            => 'collector',
            -num_repetitions => 50,
            -verbose         => 1,
    );
    my $numbers = $collector->get_numbers;
    my $strings = $collector->get_strings;
    print Dumper($numbers);
    print Dumper($strings);
}

## A rarefaction curve, with custom parameters
## In a rarefaction curve, an increasing number of randomly drawn members is sampled from the given communities and alpha diversity is calculated.
print "== Rarefaction curve\n";
if(1){
    my @alpha_types = ['observed', 'simpson', 'shannon'];
    my $rarefaction = Bio::Community::Tools::Accumulator->new(
             -metacommunity   => $meta,
             -type            => 'rarefaction',
             -num_repetitions => 50,
             -num_ticks       => 20,
             -tick_spacing    => 'linear', #logarithmic
             -alpha_types     => @alpha_types,
             -verbose         => 1,
    );
    my $numbers = $rarefaction->get_numbers;
    my $strings = $rarefaction->get_strings;
    print Dumper($numbers);
    print Dumper($strings);
    
    ## Write results to files
    #for my $i (0 .. $#alpha_types) {
    #    my $alpha_type = $alpha_types[$i];
    #    my $out_file = "rarefaction_$alpha_type.txt";
    #    print "   Writing accumulation curve to file '$out_file'\n";
    #    open my $out, '>', $out_file or die "Error: Could not write file '$out_file'\n";
    #    print $out $strings->[$i];
    #    close $out;
    #}
}

## String for the desired type of alpha diversity ('observed' by default).
## http://search.cpan.org/~fangly/Bio-Community-0.001004/lib/Bio/Community/Alpha.pm
#  Richness (or estimated number of species):
#    * observed :  C<S>
#    * menhinick:  C<S/sqrt(n)>, where C<n> is the total counts (observations).
#    * margalef : C<(S-1)/ln(n)>
#    * chao1    : Bias-corrected chao1 richness, C<S+n1*(n1-1)/(2*(n2+1))>
#                 where C<n1> and C<n2> are the number of singletons and
#                 doubletons, respectively. Particularly useful for data
#                 skewed toward the low-abundance species, e.g. microbial.
#                 Based on counts, not relative abundance.
#    * ace      : Abundance-based Coverage Estimator (ACE). Based on
#                 counts, not relative abundance.
#
#   Evenness (or equitability):
#    * buzas      : Buzas & Gibson's (or Sheldon's) evenness, C<e^H/S>.
#                   Ranges from 0 to 1.
#    * heip       : Heip's evenness, C<(e^H-1)/(S-1)>. Ranges from 0 to 1.
#    * shannon_e  : Shannon's evenness, or the Shannon-Wiener index
#                   divided by the maximum diversity possible in the
#                   community. Ranges from 0 to 1.
#    * simpson_e  : Simpson's evenness, or the Simpson's Index of Diversity
#                   divided by the maximum diversity possible in the
#                   community. Ranges from 0 to 1.
#    * brillouin_e: Brillouin's evenness, or the Brillouin's index divided
#                   by the maximum diversity possible in the community.
#                   Ranges from 0 to 1.
#    * hill_e     : Hill's C<E_2,1> evenness, i.e. Simpson's Reciprocal
#                   index divided by C<e^H>.
#    * mcintosh_e : McIntosh's evenness.
#    * camargo    : Camargo's eveness. Ranges from 0 to 1.
#
#   Indices (accounting for species abundance):
#    * shannon  : Shannon-Wiener index C<H>. Emphasizes richness and ranges
#                 from 0 to infinity.
#    * simpson  : Simpson's Index of Diversity C<1-D> (or Gini-Simpson
#                 index), where C<D> is Simpson's dominance index. C<1-D>
#                 is the probability that two individuals taken randomly
#                 are not from the same species. Emphasizes evenness and
#                 anges from 0 to 1.
#    * simpson_r: Simpson's Reciprocal Index C<1/D>. Ranges from 1 to
#                 infinity.
#    * brillouin: Brillouin's index, appropriate for small, completely
#                 censused communities. Based on counts, not relative
#                 abundance.
#    * hill     : Hill's C<N_inf> index, the inverse of the Berger-Parker
#                 dominance. Ranges from 1 to infinity.
#    * mcintosh : McIntosh's index. Based on counts, not relative abundance.
#
#   Dominance (B<not> diversity metrics since the higher their value, the
#   lower the diversity):
#    * simpson_d: Simpson's Dominance Index C<D>. Ranges from 0 to 1.
#    * berger   : Berger-Parker dominance, i.e. the proportion of the most
#                 abundant species. Ranges from 0 to 1.











