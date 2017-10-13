#!/usr/bin/perl
require 5.000;
use strict;
use File::Basename;
use Set::Light;

my $gdir = '.';
my $rdir = '.';
my $task = 1;

my  $opt_string = 'g:r:t:sSmpvxdh';
our %opt;

use Getopt::Std;
getopts("$opt_string", \%opt) or &usage;
&usage if $opt{h};
&usage if $#ARGV < 0;
if ($opt{g}) {$gdir = $opt{g}; $gdir =~ s/\/$//}
if ($opt{r}) {$rdir = $opt{r};}
if ($opt{t}) {$task = $opt{t}}
if ($task !~ /[123]/) {&usage}

## Initialize target classes using names of rule files
opendir DIR, $rdir or die "Invalid rule directory $rdir: $!";
my @target_class =
    grep { $_ ne '.' && $_ ne '..' } # filter directories
    map { basename($_, ('.rule')) } # get portion of filename before .rule extension
    readdir DIR;
closedir DIR;

## functions for equivalency checking
my $fn_eq_span  = \&eq_span_hard;;
my $fn_eq_class = \&eq_class_hard;
my $fn_eq_args  = \&eq_args_hard;
my $fn_eq_rargs = \&eq_args_hard;

## for total scoring
#  - initialized only once.
my (%tnum_gold, %tnum_mgold, %tnum_answer, %tnum_manswer); # number of golds/matched golds/answers/matched answers
foreach (@target_class) {$tnum_gold{$_} = $tnum_answer{$_} = $tnum_mgold{$_} = $tnum_manswer{$_} = 0}

my ($num_t2arg, $num_t3stat) = (0, 0); # number of task 2 arguments / task 3 statements

## for FPs and FNs
my (@FP, @FN) = ((), ());


## Variables which are file-specific.
#  - they are referenced globally.
#  - should be initialized for every file.

## for storing annotation
my ($text, $textlen, @textpic);
my (%protein, %gold, %gold_site, %equiv, %answer, %answer_site);
my (%rgold, %ranswer);   # raw data of gold and answer annotations

## for local scoring
my ($num_gold, $num_mgold, $num_answer, $num_manswer);
my (%num_gold, %num_mgold, %num_answer, %num_manswer); # number of golds/matched golds/answers/matched answers


my $fstem; # $fstem is globally referenced to know what exact file is under processing.
foreach my $fname (@ARGV) {
    if ($fname =~ /([^\/]+)\.ann$/) {$fstem = $1}
    else {warn "unrecognizable filename: $fname.\n"; next}

    ## initialization of file-specific global variables
    ($text, $textlen, @textpic) = ('', 0, ());
    (%protein, %gold, %gold_site, %equiv, %answer, %answer_site) = ();
    (%rgold, %ranswer) = ();
    ($num_gold, $num_mgold, $num_answer, $num_manswer) = (0, 0, 0, 0);
    foreach (@target_class) {
        $num_gold{$_} = $num_answer{$_} = $num_mgold{$_} = $num_manswer{$_} = 0
    }

    ## relation loading
    # verify the length of the text file
    if (!($textlen = &read_text_file("$gdir/$fstem.txt", $text))) {next}

    # verify the number of gold/predicted relations in the ann files
    if (($num_gold   = &read_ann_file("$gdir/$fstem.ann", 'G', $task)) < 0) {next}
    if (($num_answer = &read_ann_file($fname,          , 'A', $task)) < 0) {next}

    ## set matching methods
    #$fn_eq_span  = &eq_span_soft;

    ## Relation matching
    &count_match;

    # debugging message
    if ($opt{d}) {
    	foreach (@target_class) {
    	    if ($num_manswer{$_} != $num_mgold{$_})  {warn "inconsistent number of matched events: [$fstem] [$_]\t$num_manswer{$_} vs. $num_mgold{$_}\n"}
    	    if ($num_manswer{$_} != $num_answer{$_}) {warn "not perfect precision: [$fstem] [$_] $num_manswer{$_} / $num_answer{$_}\n"}
    	    if ($num_mgold{$_}   != $num_gold{$_})   {warn "not perfect recall   : [$fstem] [$_] $num_mgold{$_} / $num_gold{$_}\n"}
    	} # foreach
    } # if

    ## adjustment for duplication
    foreach (@target_class) {
	if ($num_manswer{$_} > $num_mgold{$_}) {
	    my $num_danswer = $num_manswer{$_} - $num_mgold{$_};
	    $num_answer{$_}  -= $num_danswer;
	    $num_manswer{$_} -= $num_danswer;
	    if ($opt{v}) {warn "$num_danswer relations(s) have been discarded due to an equivanlency by the approximate matching: [$fstem]\n"}
	} # if
    } # foreach

    ## totalling
    foreach (@target_class) {
	$tnum_gold{$_}    += $num_gold{$_};
	$tnum_answer{$_}  += $num_answer{$_};
	$tnum_mgold{$_}   += $num_mgold{$_};
	$tnum_manswer{$_} += $num_manswer{$_};
    } # foreach
} # foreach

if (($task == 2) && ($num_t2arg == 0)) {die "no argument that belongs to task 2 found.\n"}

if ($task =~ /[12]/) {

    my ($tnum_gold, $tnum_mgold, $tnum_answer, $tnum_manswer) = (0, 0, 0, 0);

    foreach (@target_class) {
    	&report ($_, $tnum_gold{$_}, $tnum_mgold{$_}, $tnum_answer{$_}, $tnum_manswer{$_});
    	$tnum_gold += $tnum_gold{$_}; $tnum_mgold += $tnum_mgold{$_};
    	$tnum_answer += $tnum_answer{$_}; $tnum_manswer += $tnum_manswer{$_};
    } # foreach
    &report ('==[REL-TOTAL]==', $tnum_gold, $tnum_mgold, $tnum_answer, $tnum_manswer);
    print STDOUT "------------------------------------------------------------------------------------\n";

    my ($gnum_gold, $gnum_mgold, $gnum_answer, $gnum_manswer) = ($tnum_gold, $tnum_mgold, $tnum_answer, $tnum_manswer);

    &report ('==[ALL-TOTAL]==', $gnum_gold, $gnum_mgold, $gnum_answer, $gnum_manswer);
    print STDOUT "------------------------------------------------------------------------------------\n";
} # if (task == 1 or 2)

if ($opt{x}) {
    if (@FP) {print "\n"}
    foreach (@FP) {print "[FP]  $_\n"}
    if (@FN) {print "\n"}
    foreach (@FN) {print "[FN]  $_\n"}
} # if

exit;


my ($c, $g, $mg, $w, $mw, $r, $p, $f);

format STDOUT_TOP =
-----------------------------------------------------------------------------------------------------------
     Event Class                                 gold (match)   answer (match)   recall    prec.   fscore
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

sub storeFP {
    my $tanno = $ranswer{$_[0]};
    #while ($tanno =~ /:(T.+)/) {
    #    my $tspan = &tspan($1, \%answer);
    #    $tanno =~ s/:$1/:$tspan/;
    #    print("term annotation: $tanno\n");
    #    exit 0;
    #}
    push @FP, "$fstem#$tanno";
} # storeFP

sub storeFN {
    my $tanno = $rgold{$_[0]};
    #while ($tanno =~ /:(T.+)/) {
    #    my $tspan = &tspan($1, \%gold);
    #    $tanno =~ s/:$1/:$tspan/;
    #}
    push @FN, "$fstem#$tanno";
} # storeFN

sub tspan {
    my ($id, $rh_anno) = @_;
    my ($beg, $end);
    if    (($id =~ /^T/) && $protein{$id})   {($beg, $end) = (${$protein{$id}}[1],   ${$protein{$id}}[2])}
    elsif (($id =~ /^T/) && $rh_anno->{$id}) {($beg, $end) = (${$rh_anno->{$id}}[1], ${$rh_anno->{$id}}[2])}
    else  {return $id}

    return '"' . substr ($text, $beg, $end-$beg) . '"'. "[$beg-$end]";
} # tspan

sub count_match {
    my %cnt_manswer = (); # count matches of answer annotation instances.
    my %cnt_mgold   = (); # count matches of gold annotation instances.

    my @answer = ();
    foreach (keys %answer) {
        if (/^[R]/) {
            push @answer, $_;
            $cnt_manswer{$_} = 0
        }
    }
    my @gold   = ();
    foreach (keys %gold)   {
        if (/^[R]/) {
            push @gold,   $_;
            $cnt_mgold{$_} = 0
        }
    }

    #  for each answer,
    foreach my $aid (@answer) {
    	# search for golds which match it.
    	foreach my $gid (@gold) {
    	    # when found,
    	    if (eq_relation($aid, $gid)) {
        		$cnt_manswer{$aid}++;
        		$cnt_mgold{$gid}++;
    	    } # if
    	} # foreach
    } # foreach

    # update per-class statistics & store
    foreach (@answer) {
        if ($cnt_manswer{$_} > 0) {
            $num_manswer{${$answer{$_}}[0]}++;
        }
    }
    foreach (@gold) {
        if ($cnt_mgold{$_}   > 0) {
            $num_mgold{${$gold{$_}}[0]}++;
        }
    }

    # store FPs and FNs
    foreach (@answer) {
        if ($cnt_manswer{$_} < 1) {
            &storeFP($_);
        }
    }
    foreach (@gold)   {
        if ($cnt_mgold{$_}   < 1) {
            &storeFN($_);
        }
    }
} # count_match

sub eq_relation {
    my ($aeid, $geid) = @_;
    #print("Comparing $aeid with $geid\n");
    if    (($aeid =~ /^R/) && ($geid =~ /^R/)) {
        #print("Both have Rs");
        if ($fn_eq_class->($aeid, $geid) &&
    	    $fn_eq_args->($aeid, $geid)) {
                #print("$aeid and $geid are equivalent");
                return 1
        }
    } # if

    else {return 0}
} # eq_relation


sub eq_revent {
    my ($aeid, $geid) = @_;
    if ($aeid !~ /^E/) {warn "non-event annotation: $aeid.\n"; return 0}
    if ($geid !~ /^E/) {warn "non-event annotation: $geid.\n"; return 0}

    if ($fn_eq_class->($aeid, $geid) &&
	$fn_eq_span->($aeid, $geid) &&
	$fn_eq_rargs->($aeid, $geid)) {return 1}

    else {return 0}
} # eq_event


sub eq_entity {
    my ($aeid, $geid) = @_;
    if ($aeid !~ /^T/) {warn "[eq_entity] non-entity annotation: $aeid.\n"; return 0}
    if ($geid !~ /^T/) {warn "[eq_entity] non-entity annotation: $geid.\n"; return 0}

    if ($fn_eq_class->($aeid, $geid) && $fn_eq_span->($aeid, $geid)) {return 1}
    else {return 0}
} # eq_entity


sub eq_span_hard {
    my ($aid, $gid) = @_;
    my ($abeg, $aend, $gbeg, $gend) = (-1, -1, -1, -1);

    if (($aid =~ /^T/) && $protein{$aid}) {return ($aid eq $gid)}

    if    ($aid =~ /^T/) {$abeg = ${$answer{$aid}}[1]; $aend = ${$answer{$aid}}[2]}
    elsif ($aid =~ /^E/) {$abeg = ${$answer{${$answer{$aid}}[1]}}[1]; $aend = ${$answer{${$answer{$aid}}[1]}}[2]}

    if    ($gid =~ /^T/) {$gbeg = ${$gold{$gid}}[1];   $gend = ${$gold{$gid}}[2]}
    elsif ($gid =~ /^E/) {$gbeg = ${$gold{${$gold{$gid}}[1]}}[1];     $gend = ${$gold{${$gold{$gid}}[1]}}[2]}

    if (($abeg < 0) || ($gbeg < 0)) {warn "failed to find the span: $fstem ($aid, $gid)\n"; return ''}

    return (($abeg == $gbeg) && ($aend == $gend));
} # eq_span_hard


sub eq_span_soft {
    my ($aid, $gid) = @_;

    my ($abeg, $aend, $gbeg, $gend) = (-1, -1, -2, -2);

    if (($aid =~ /^T/) && $protein{$aid}) {return ($aid eq $gid)}

    if    ($aid =~ /^T/) {$abeg = ${$answer{$aid}}[1]; $aend = ${$answer{$aid}}[2]}
    elsif ($aid =~ /^E/) {$abeg = ${$answer{${$answer{$aid}}[1]}}[1]; $aend = ${$answer{${$answer{$aid}}[1]}}[2]}

    if    ($gid =~ /^T/) {$gbeg = ${$gold{$gid}}[1];   $gend = ${$gold{$gid}}[2]}
    elsif ($gid =~ /^E/) {$gbeg = ${$gold{${$gold{$gid}}[1]}}[1];     $gend = ${$gold{${$gold{$gid}}[1]}}[2]}

    if (($abeg < 0) || ($gbeg < 0)) {warn "failed to find the span: $fstem ($aid, $gid)\n"; return ''}

    ($gbeg, $gend) = &expand_span($gbeg, $gend);
    return (($abeg >= $gbeg) && ($aend <= $gend));
} # eq_span_soft


sub eq_span_soft_notrigger {
    my ($aid, $gid) = @_;
    if (($aid =~ /^E/) && ($gid =~ /^E/)) {return 1}
    return &eq_span_soft($aid, $gid);
} # eq_span_soft_notrigger


# expand an entity span
# it refers to global variables $text and @entity
sub expand_span  {
    my ($beg, $end) = @_;

    my $ebeg = $beg - 2;
    while (($ebeg >= 0)        && (substr ($text, $ebeg, 1) !~ /[ .!?,"']/) && ($textpic[$ebeg] ne 'E')) {$ebeg--} # '"
    $ebeg++;

    my $eend = $end + 2;
    while (($eend <= $textlen) && (substr ($text, $eend-1, 1) !~ /[ .!?,"']/) && ($textpic[$eend-1] ne 'E')) {$eend++} # '"
    $eend--;

#    warn "\n", substr ($text, $ebeg-5, $eend-$ebeg+10), "\n";
#    for(my $i = $ebeg-5; $i< $eend+5; $i++) {
#	if ($textpic[$i]) {warn $textpic[$i]}
#	else {warn ' '}
#    } # for ($i)
#    warn "\n";
#    warn substr ($text, $beg, $end-$beg), "  ===> ", substr ($text, $ebeg, $eend-$ebeg), "\n";

    return ($ebeg, $eend);
} # expand_span


sub eq_class_hard {
    my ($aid, $gid) = @_;
    #print("Comparing classes of $aid and $gid\n");
    if ($answer{$aid})  {
        #print("Answer class: ${$answer{$aid}}[0]\n");
        #print("Gold class: ${$gold{$gid}}[0]\n");
        if (${$answer{$aid}}[0] eq ${$gold{$gid}}[0]) {
            #print("Classes are equal!\n");
            return 1;
        }
        else {
            next;
        }
    }
    else  {
        #print("Classes are not equal =(\n");
        return 0;
    }
} # eq_class_hard


sub eq_class_soft {
    my ($aid, $gid) = @_;
    if    ($protein{$aid}) {return ($aid eq $gid)}
    elsif ($answer{$aid})  {
	my $aclass = ${$answer{$aid}}[0];
	my $gclass = ${$gold{$gid}}[0];
	$aclass =~ s/^Positive_r/R/; $gclass =~ s/^Positive_r/R/;
	$aclass =~ s/^Negative_r/R/; $gclass =~ s/^Negative_r/R/;
	$aclass =~ s/^Transcription$/Gene_expression/; $gclass =~ s/^Transcription/Gene_expression/;
	return ($aclass eq $gclass);
    } # elsif
    else  {return 0}
} # eq_class_soft


sub eq_args_hard {
    my ($aeid, $geid) = @_;

    my @answer_arg = @{$answer{$aeid}}[1..2];
    my $answer_arg1 = shift @answer_arg;
    my $answer_arg2 = shift @answer_arg;

    my ( $answer_arg1 ) = $answer_arg1=~ /(\:.*)\s*$/;
    my ( $answer_arg2 ) = $answer_arg2=~ /(\:.*)\s*$/;

    my @gold_arg =   @{$gold{$geid}}[1..2];
    my $gold_arg1 = shift @gold_arg;
    my $gold_arg2 = shift @gold_arg;

    my ( $gold_arg1 ) = $gold_arg1=~ /(\:.*)\s*$/;
    my ( $gold_arg2 ) = $gold_arg2=~ /(\:.*)\s*$/;

    my @gold_args = sort ($gold_arg1, $gold_arg2);
    my @answer_args = sort ($answer_arg1, $answer_arg2);

    if ( @gold_args ~~ @answer_args ) {
        return 1;
    }
    else {
        return 0;
    }
} # eq_args_hard


sub eq_args_soft {
    my ($aeid, $geid) = @_;

    my @answer_arg = @{$answer{$aeid}};
    my $aetype = shift @answer_arg;
    shift @answer_arg;
    while ($answer_arg[-1] !~ /^Theme:/) {pop @answer_arg}

    my @gold_arg =   @{$gold{$geid}};
    my $getype = shift @gold_arg;
    shift @gold_arg;
    while ($gold_arg[-1] !~ /^Theme:/) {pop @gold_arg}

    ## compare argument lists as ordered lists.
    if ($#answer_arg != $#gold_arg) {return ''}
    for (my $i = 0; $i <= $#answer_arg; $i++) {
	my ($aatype, $aaid) = split /:/, $answer_arg[$i];
	my ($gatype, $gaid) = split /:/, $gold_arg[$i];

	# both have to be either t-entities or events
	if (substr($aaid, 0, 1) ne substr($gaid, 0, 1))  {return ''}
	if (($aaid =~ /^E/) && !&eq_revent($aaid, $gaid)) {return ''}
	if (($aaid =~ /^T/) && !&eq_entity($aaid, $gaid)) {return ''}
    } # for

    return 1;
} # eq_args_soft


## representation of annotations
# t-entities:          TID (entity_type, beg, end)
#
# event annotation:    EID (event-type, event_entity_id, arg_type:arg_id, arg_type:arg_id, ...)
#                     * order of arguments: theme, cause, site, csite, AtLoc, ToLoc
#                     * linear order between themes
#                     * site may be numbered to indicate the specific theme
#
#  Modifier:           MID (mod_type, '', (Theme, $arg))

sub get_target_classes ($) {
    my $ruledir = $_[0];
    my @files = <$ruledir/*.rule>;
}

sub read_text_file ($$) {
    my ($fname) = $_[0];
    $_[1] = '';     # text, output variable

    if (!open (FILE, "<", $fname)) {warn "cannot open the file: $fname\n"; return ''}
    while (<FILE>) {$_[1] .= $_}
    close (FILE);

    return length $_[1];
} # read_text_file

sub read_ann_file ($$$) {
    #fname = gold training file
    #mode  = G or A, determines whether we're reading the
    #        gold test data or our prediction (Answer/A)
    #task  = ???
    my ($fname, $mode, $task) = @_; # rh: reference to hash

    if (!open (FILE, "<", $fname)) {warn "cannot open the ann file: $fname\n"; return -1}
    my @line = <FILE>; chomp (@line);
    close (FILE);

    my ($rh_anno, $rh_site, $rh_ranno, $rh_num_relation); # reference to hash

    #All variables are initialized to some kind of hash
    if ($mode eq 'G') {
        $rh_anno = \%gold;
        $rh_site = \%gold_site;
        $rh_ranno = \%rgold;
        $rh_num_relation = \%num_gold
    }
    else {
        $rh_anno = \%answer;
        $rh_site = \%answer_site;
        $rh_ranno = \%ranswer;
        $rh_num_relation = \%num_answer
    }

    if ($mode eq 'G') {
        #Loops over each line in the ann file
        #Reads relations
        foreach (@line) {
            my ($id, $exp) = split /\t/;
        	$rh_ranno->{$id} = $_;

        	if (/^T/) {

                my @arg = split ' ', $exp;

                my $type = @arg[0];

        	    $rh_anno->{$id} = $type;
            } # if

        } # foreach

        foreach (@line) {
            my ($id, $exp) = split /\t/;

        	if (/^R/) {

                my @arg = split ' ', $exp;

                my $type = @arg[0];
                my @arg = @arg[1..$#arg];

                #my ($type, $tid) = split ':', shift @arg;
                my @newarg = ();
                my @argtypes = ();
        	    foreach (@arg) {
            		my ($atype, $aid) = split ':';

                    my $athemetype = $rh_anno->{$aid};
                    push @argtypes, $athemetype;

            		if ($equiv{$aid}) {
                        $aid = $equiv{$aid}
                    }

            		push @newarg, "$atype:$aid";
            	} # foreach

                @argtypes = sort @argtypes;
                my $typea = lc(@argtypes[0]);
                my $typeb = lc(@argtypes[1]);
                $type = lc"$typea$type$typeb";
                $type =~ tr/-//d;

                $rh_anno->{$id} = [$type, @newarg];
            } # if

        } # foreach
    } # if ($mode eq 'G')
    else {
        foreach (@line) {
            my ($id, $exp) = split /\t/;
            $rh_ranno->{$id} = $_;

        	if (/^R/) {
                my @arg = split ' ', $exp;

                my $type = @arg[0];
                my @arg = @arg[1..$#arg];

                #my ($type, $tid) = split ':', shift @arg;
                my @newarg = ();
        	    foreach (@arg) {
            		my ($atype, $aid) = split ':';

            		if ($equiv{$aid}) {
                        $aid = $equiv{$aid}
                    }

            		push @newarg, "$atype:$aid";
            	} # foreach

                $rh_anno->{$id} = [$type, @newarg];
            } # if

        } # foreach
    }

    my @rlist = grep /^[R]/, keys %{$rh_anno};

    # detect and remove duplication by Simplication
    if ($mode eq 'G') {
    	## sort relations
    	my @newrlist = ();
    	my %added = ();
    	my %remain = ();
    	foreach (@rlist) {
            $remain{$_} = 1
        }
    	while (%remain) {
    	    my $changep = 0;
    	    foreach (keys %remain) {
    		my @earg = grep /:E[0-9-]+$/, @{$rh_anno->{$_}};
    		my @eaid = map {(split /:/)[1]} @earg;
    		my $danglingp = 0;
    		foreach (@eaid) {
    		    if (!$added{$_}) {$danglingp = 1; last}
    		} # foreach
    		if (!$danglingp) {push @newrlist, $_; $added{$_} = 1; delete $remain{$_}; $changep = 1}
    	    } # foreach
    	    if (!$changep) {
    		if ($opt{v}) {warn "circular reference: [$fstem] ", join (', ', keys %remain), "\n"}
    		push @newrlist, keys %remain;
    		%remain = ();
    	    } # if
    	} # while

    	@rlist = @newrlist;

    	my %equiv = ();		# 'equiv' locally defined only for gold data
    	my %relationexp = (); # for checking of relation duplication
    	foreach my $eid (@rlist) {
    	    # get relation expression
    	    foreach (@{$rh_anno->{$eid}}) {
    		if (!/:/) {next}
    		my ($atype, $aid) = split /:/;
    		if ($equiv{$aid}) {$aid = $equiv{$aid}}
    		$_ = "$atype:$aid";
    	    } # foreach

    	    my $relationexp = join ',', @{$rh_anno->{$eid}};

    	    # check duplication
    	    if (my $did = $relationexp{$relationexp}) {
    		delete $rh_anno->{$eid};
    		$equiv{$eid} = $did;
    		if ($opt{v}) {warn "[$fstem] $eid is equivalent to $did => removed.\n"}
    	    } # if
    	    else {$relationexp{$relationexp} = $eid}
    	} # foreach

    	@rlist = grep /^[R]/, keys %{$rh_anno};
    } # if (mode eq 'G')


    # detect and remove duplication by Equiv
    if ($mode eq 'A') {
    	## sort relations
    	my @newrlist = ();
    	my %added = ();
    	my %remain = ();
    	foreach (@rlist) {$remain{$_} = 1}
    	while (%remain) {
    	    my $changep = 0;
    	    foreach (keys %remain) {
        		my @earg = grep /:E[0-9-]+$/, @{$rh_anno->{$_}};
        		my @eaid = map {(split /:/)[1]} @earg;
        		my $danglingp = 0;
        		foreach (@eaid) {
        		    if (!$added{$_}) {$danglingp = 1; last}
        		} # foreach
        		if (!$danglingp) {
                    push @newrlist, $_;
                    $added{$_} = 1;
                    delete $remain{$_};
                    $changep = 1;
                }
    	    } # foreach
    	    if (!$changep) {
        		if ($opt{v}) {
                    warn "circular reference: [$fstem] ", join (', ', keys %remain), "\n"
                }
        		push @newrlist, keys %remain;
        		%remain = ();
    	    } # if
    	} # while

    	@rlist = @newrlist;

    	my %relationexp = (); # for checking of relation duplication
    	foreach my $eid (@rlist) {
    	    # get relation expression
    	    foreach (@{$rh_anno->{$eid}}) {
    		if (!/:/) {next}
    		my ($atype, $aid) = split /:/;
    		if ($equiv{$aid}) {$aid = $equiv{$aid}}
    		$_ = "$atype:$aid";
    	    } # foreach

    	    my $relationexp = join ',', @{$rh_anno->{$eid}};

    	    # check duplication
    	    if (my $did = $relationexp{$relationexp}) {
    		delete $rh_anno->{$eid};
    		$equiv{$eid} = $did;
    		if ($opt{v}) {warn "[$fstem] $eid is equivalent to $did => removed.\n"}
    	    } # if
    	    else {$relationexp{$relationexp} = $eid}
    	} # foreach

    	@rlist = grep /^[R]/, keys %{$rh_anno};
    } # if (mode eq 'A')

    # get statistics
    my $num_relation = 0;
    foreach my $eid (@rlist) {
    	my $type = ${$rh_anno->{$eid}}[0];
    	$rh_num_relation->{$type}++; $num_relation++;
    } # foreach

    return $num_relation;
} # read_ann_file



sub usage {
    warn << "EOF";

[ann-evaluate]
last updated by khirsinger\@student.unimelb.edu.au on 3 June 2016.


<DESCRIPTION>
Re-written version of the a2-evaluate.pl script for Variome relation
annotation (ann) files.

<USAGE>
$0 [-$opt_string] ann_file(s)


<OPTIONS>
-g gold_dir specifies the 'gold' directory (default = $gdir)
-r rule_dir specifies the 'rule' directory (default = $rdir)
-t task     specifies the task type (1, 2, or 3; default = $task)
-s          tells it to perform a soft matching for the boundary of triggers and entities.
-S          tells it to ignore event triggers and perform a soft matching the boundary of entities.
-p          tells it to perform an approximate recursive matching.
-v          verbose output.
-x          output false positives/negatives
-d          debugging message.


<REFERENCE>
https://sites.google.com/site/bionlpst/

EOF
      exit;
} # usage
