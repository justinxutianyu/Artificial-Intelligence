#!/usr/bin/perl -w

my $rdir = '.';

my  $opt_string = 'r:';
our %opt;

use File::Basename;
use Getopt::Std;

getopts("$opt_string", \%opt);

if ($opt{r}) {$rdir = $opt{r};}

## Initialize target classes using names of rule files
opendir DIR, $rdir or die "Invalid rule directory $rdir: $!";
my @target_class =
    grep { $_ ne '.' && $_ ne '..' } # filter directories
    map { basename($_, ('.rule')) } # get portion of filename before .rule extension
    readdir DIR;
closedir DIR;

## Initialize all scores to zero
my %gold_scores = ();
my %match_scores = ();
my %ans_scores = ();
foreach my $class (@target_class) {
    $gold_scores->{$class} = 0; # Number of predictions in 'gold' test set
    $match_scores->{$class} = 0; # Number of matching predictions
    $ans_scores->{$class} = 0; # Overall number of predictions
}

#Loop over eval files and read the results
opendir DIR, "./eval" or die "$!";
foreach my $file (readdir DIR){
    next unless $file =~ /(.*)\.eval$/;
    my $prefix = $1;
    open L, "./eval/$file" or die "cannot open the evaluation file $file: $!";
    while(<L>){
    	  s/\r$//;
        foreach my $class (@target_class) {
            #    Event Class  gold        (match)       answer      (match)
            if(/\s*($class)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
                $gold_scores->{$class} += $2;
                $match_scores->{$class} += $5;
                $ans_scores->{$class} += $4;
            }
        }
    }
}

#Sum all scores to obtain overall score
my ($rel_gold, $rel_ans, $rel_match) = (0, 0, 0);
foreach my $class (@target_class) {
    $rel_gold += $gold_scores->{$class};
    $rel_ans += $ans_scores->{$class};
    $rel_match += $match_scores->{$class};
}

#all total
my $all_p = sprintf "%.2f", 100*(($rel_match)/($rel_ans));
my $all_r = sprintf "%.2f", 100*(($rel_match)/($rel_gold));
my $all_f = sprintf "%.2f", 2*$all_p*$all_r/($all_p+$all_r);
my $all_gold = $rel_gold;
my $all_ans = $rel_ans;
my $all_match = $rel_match;

foreach my $class (@target_class) {
    &report (
        $class,
        $gold_scores->{$class},
        $match_scores->{$class},
        $ans_scores->{$class},
        $match_scores->{$class}
    );
}
print "\n\n";
print "Totals\n\n";
print "Precision:                      $all_p\n";
print "Recall:                         $all_r\n";
print "F-Score:                        $all_f\n";
print "\nNumber of Gold Relations:       $all_gold\n";
print "Number of Predicted Relations:  $all_ans\n";
print "Number of Matching Predictions: $all_match\n";

close DIR;

exit;

my (
    $c, $g, $mg, $w, $mw, $r, $p, $f
);

format STDOUT_TOP =
-----------------------------------------------------------------------------------------------------------
                 Event Class                     gold (match)    answer (match)   recall    prec.   fscore
-----------------------------------------------------------------------------------------------------------
.

format STDOUT =
  @||||||||||||||||||||||||||||||||||||||||||    @#### (@####)    @#### (@####)   @##.##   @##.##   @##.##
$c, $g, $mg, $w, $mw, $r, $p, $f
.

sub report ($$$$$) {
    ($c, $g, $mg, $w, $mw) = @_;
    ($r, $p, $f) = &accuracy ($g, $mg, $w, $mw);
    write ();
} # report

sub accuracy {
    my ($gold, $mgold, $answer, $manswer) = @_;

    my $rec = ($gold)?   $mgold   /   $gold : 0;
    my $pre = ($answer)? $manswer / $answer : 0;
    my $f1s = ($pre + $rec)? (2 * $pre * $rec) / ($pre + $rec) : 0;

    return ($rec * 100, $pre * 100, $f1s * 100);
} # accuracy
