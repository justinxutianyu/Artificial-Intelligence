#!/usr/bin/perl -w
# Usage:   ./create_index_trigger_tees.pl in_dir
# Example: ./create_index_trigger_tees.pl /home/davidm/BioNLP2013-Data/Data/TEES_output

use strict;

use vars qw (@File $f %H $i $j $k $l @F %G $e %Ind $w);

if (not defined $ARGV[0]) {
    die "Usage:   ./create_index_trigger_tees.pl in_dir\n";}

my $in_d = $ARGV[0];

undef %Ind;

opendir(D,"$in_d")||next;
@File = grep /\.a2$/,readdir D;
closedir(D);

foreach $f (@File) {
    open(I,"$in_d/$f")||die;
    while(<I>) {
	chomp;
	if (s/^X\d+\t(T\d+) conf //) {
	    $e = $1;
	    @F = split(/ /,$_);
	    undef %H;
	    foreach (@F) {
		$_ = &max_sc($_);
		if ((not defined $H{$e})||
		    ($_ < $H{$e})) {
		    $H{$e} = $_;
		}
	    }
	    $_ = int $H{$e};
	    $Ind{$_}{$f}{$e} = 1;
	}
    }
    close(I);
}

foreach $w (sort {$b<=>$a} keys %Ind) {
    print "$w";
    foreach $f (keys %{$Ind{$w}}) {
	@F = keys %{$Ind{$w}{$f}};
	$_ = join ":",@F;
	print "\t$f:$_";
    }
    print "\n";
}




sub max_sc {

    my @F = split(/\,/,$_[0]);
    my $max_sc = 0;			
    foreach (@F) {
	/^(.*?)\:(.*)$/;
	if ($2 > $max_sc) {
	    $max_sc = $2;
	}
    }
    return $max_sc;
}
