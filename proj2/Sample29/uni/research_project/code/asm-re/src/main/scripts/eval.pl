#!/usr/bin/perl -w

opendir DIRA, "./prediction" or die "$!";
foreach my $file (readdir DIRA){ 
    next unless $file =~ /(.*)\.a2$/;
    my $prefix = $1;
    #print $prefix,"\n";
    system "perl a2-normalize.pl -g gold_train_dev -u ./prediction/$file";
    system "perl a2-evaluate.pl -g gold_train_dev -sp ./prediction/$file >eval/$prefix.eval";
    #unlink("./prediction/$file"); 
}   
close DIRA;
