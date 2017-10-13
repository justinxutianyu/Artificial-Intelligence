#!/usr/bin/perl -w

my ($Gene_expression_gold, $Gene_expression_match, $Gene_expression_ans);
my ($Transcription_gold, $Transcription_match, $Transcription_ans);
my ($Protein_catabolism_gold, $Protein_catabolism_match, $Protein_catabolism_ans);
my ($Phosphorylation_gold, $Phosphorylation_match, $Phosphorylation_ans);
my ($Localization_gold, $Localization_match, $Localization_ans);
my ($Acetylation_gold, $Acetylation_match, $Acetylation_ans);
my ($Deacetylation_gold, $Deacetylation_match, $Deacetylation_ans);
my ($Protein_modification_gold, $Protein_modification_match, $Protein_modification_ans);
my ($Ubiquitination_gold, $Ubiquitination_match, $Ubiquitination_ans);
my ($Binding_gold, $Binding_match, $Binding_ans);
my ($Regulation_gold, $Regulation_match, $Regulation_ans); 
my ($Positive_regulation_gold, $Positive_regulation_match, $Positive_regulation_ans); 
my ($Negative_regulation_gold, $Negative_regulation_match, $Negative_regulation_ans);   

opendir DIR, "./eval" or die "$!";
foreach my $file (readdir DIR){ 
    next unless $file =~ /(.*)\.eval$/;
    #next unless $file =~ /(1335418).eval$/;
    my $prefix = $1;
    open L, "./eval/$file" or die "cannot open the evaluation file $file: $!";
    while(<L>){
    	  s/\r$//;
        if(/\s*(Gene\_expression)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Gene_expression_gold += $2;
            $Gene_expression_match += $5;
            $Gene_expression_ans += $4; 
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        } 
    	  elsif(/\s*(Transcription)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Transcription_gold += $2;
            $Transcription_match += $3;
            $Transcription_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Protein\_catabolism)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Protein_catabolism_gold += $2;
            $Protein_catabolism_match += $3;
            $Protein_catabolism_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        } 
        elsif(/\s*(Phosphorylation)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Phosphorylation_gold += $2;
            $Phosphorylation_match += $3;
            $Phosphorylation_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Localization)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Localization_gold += $2;
            $Localization_match += $3;
            $Localization_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Acetylation)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Acetylation_gold += $2;
            $Acetylation_match += $3;
            $Acetylation_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Deacetylation)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Deacetylation_gold += $2;
            $Deacetylation_match += $3;
            $Deacetylation_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Protein\_modificatio)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Protein_modification_gold += $2;
            $Protein_modification_match += $3;
            $Protein_modification_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Ubiquitination)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Ubiquitination_gold += $2;
            $Ubiquitination_match += $3;
            $Ubiquitination_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
        elsif(/\s*(Binding)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Binding_gold += $2;
            $Binding_match += $3;
            $Binding_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }       
        elsif(/\s*(Regulation)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Regulation_gold += $2;
            $Regulation_match += $3;
            $Regulation_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }     
        elsif(/\s*(Positive\_regulation)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Positive_regulation_gold += $2;
            $Positive_regulation_match += $3;
            $Positive_regulation_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }     
        elsif(/\s*(Negative\_regulation)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*(\d+)\s*\(\s*(\d+)\s*\)\s*/){
            $Negative_regulation_gold += $2;
            $Negative_regulation_match += $3;
            $Negative_regulation_ans += $4;
            #if($3 != $5){ print "event number matched is wrong:\t$file\t$1"; exit; }
        }
    }        
}   

#calculate statistics
#each class
#my $Gene_expression_p = sprintf "%.2f", 100*$Gene_expression_match/$Gene_expression_ans;
#my $Gene_expression_r = sprintf "%.2f", 100*$Gene_expression_match/$Gene_expression_gold;
#my $Gene_expression_f = sprintf "%.2f", 2*$Gene_expression_p*$Gene_expression_r/($Gene_expression_p+$Gene_expression_r);

#my $Transcription_p = sprintf "%.2f", 100*$Transcription_match/$Transcription_ans;
#my $Transcription_r = sprintf "%.2f", 100*$Transcription_match/$Transcription_gold;
#my $Transcription_f = sprintf "%.2f", 2*$Transcription_p*$Transcription_r/($Transcription_p+$Transcription_r);

#my $Protein_catabolism_p = sprintf "%.2f", 100*$Protein_catabolism_match/$Protein_catabolism_ans;
#my $Protein_catabolism_r = sprintf "%.2f", 100*$Protein_catabolism_match/$Protein_catabolism_gold;
#if ($Protein_catabolism_r == 0 and $Protein_catabolism_p == 0 ){$Protein_catabolism_f = sprintf "%.2f", 0;}
#else{$Protein_catabolism_f = sprintf "%.2f", 2*$Protein_catabolism_p*$Protein_catabolism_r/($Protein_catabolism_p+$Protein_catabolism_r);}

#my $Phosphorylation_p = sprintf "%.2f", 100*$Phosphorylation_match/$Phosphorylation_ans;
#my $Phosphorylation_r = sprintf "%.2f", 100*$Phosphorylation_match/$Phosphorylation_gold;
#my $Phosphorylation_f = sprintf "%.2f", 2*$Phosphorylation_p*$Phosphorylation_r/($Phosphorylation_p+$Phosphorylation_r);

#my $Localization_p = sprintf "%.2f", 100*$Localization_match/$Localization_ans;
#my $Localization_r = sprintf "%.2f", 100*$Localization_match/$Localization_gold;
#my $Localization_f = sprintf "%.2f", 2*$Localization_p*$Localization_r/($Localization_p+$Localization_r);

#my $Binding_p = sprintf "%.2f", 100*$Binding_match/$Binding_ans;
#my $Binding_r = sprintf "%.2f", 100*$Binding_match/$Binding_gold;
#my $Binding_f = sprintf "%.2f", 2*$Binding_p*$Binding_r/($Binding_p+$Binding_r);

#my $Regulation_p = sprintf "%.2f", 100*$Regulation_match/$Regulation_ans;
#my $Regulation_r = sprintf "%.2f", 100*$Regulation_match/$Regulation_gold;
#my $Regulation_f = sprintf "%.2f", 2*$Regulation_p*$Regulation_r/($Regulation_p+$Regulation_r);

#my $Positive_regulation_p = sprintf "%.2f", 100*$Positive_regulation_match/$Positive_regulation_ans;
#my $Positive_regulation_r = sprintf "%.2f", 100*$Positive_regulation_match/$Positive_regulation_gold;
#my $Positive_regulation_f = sprintf "%.2f", 2*$Positive_regulation_p*$Positive_regulation_r/($Positive_regulation_p+$Positive_regulation_r);

#my $Negative_regulation_p = sprintf "%.2f", 100*$Negative_regulation_match/$Negative_regulation_ans;
#my $Negative_regulation_r = sprintf "%.2f", 100*$Negative_regulation_match/$Negative_regulation_gold;
#my $Negative_regulation_f = sprintf "%.2f", 2*$Negative_regulation_p*$Negative_regulation_r/($Negative_regulation_p+$Negative_regulation_r);

#two subtotals
#my $eve_p = sprintf "%.2f", 100*($Gene_expression_match+$Transcription_match+$Protein_catabolism_match+$Phosphorylation_match+$Localization_match+$Binding_match)/($Gene_expression_ans+$Transcription_ans+$Protein_catabolism_ans+$Phosphorylation_ans+$Localization_ans+$Binding_ans);
#my $eve_r = sprintf "%.2f", 100*($Gene_expression_match+$Transcription_match+$Protein_catabolism_match+$Phosphorylation_match+$Localization_match+$Binding_match)/($Gene_expression_gold+$Transcription_gold+$Protein_catabolism_gold+$Phosphorylation_gold+$Localization_gold+$Binding_gold);
#my $eve_f = sprintf "%.2f", 2*$eve_p*$eve_r/($eve_p+$eve_r);
my $eve_gold = $Gene_expression_gold+$Transcription_gold+$Protein_catabolism_gold+$Phosphorylation_gold+$Localization_gold+$Acetylation_gold+$Deacetylation_gold+$Protein_modification_gold+$Ubiquitination_gold+$Binding_gold;
my $eve_ans = $Gene_expression_ans+$Transcription_ans+$Protein_catabolism_ans+$Phosphorylation_ans+$Localization_ans+$Acetylation_ans+$Deacetylation_ans+$Protein_modification_ans+$Ubiquitination_ans+$Binding_ans;
my $eve_match = $Gene_expression_match+$Transcription_match+$Protein_catabolism_match+$Phosphorylation_match+$Localization_match+$Acetylation_match+$Deacetylation_match+$Protein_modification_match+$Ubiquitination_match+$Binding_match;


#my $reg_p = sprintf "%.2f", 100*($Regulation_match+$Positive_regulation_match+$Negative_regulation_match)/($Regulation_ans+$Positive_regulation_ans+$Negative_regulation_ans);
#my $reg_r = sprintf "%.2f", 100*($Regulation_match+$Positive_regulation_match+$Negative_regulation_match)/($Regulation_gold+$Positive_regulation_gold+$Negative_regulation_gold);
#my $reg_f = sprintf "%.2f", 2*$reg_p*$reg_r/($reg_p+$reg_r);
my $reg_gold = $Regulation_gold+$Positive_regulation_gold+$Negative_regulation_gold;
my $reg_ans = $Regulation_ans+$Positive_regulation_ans+$Negative_regulation_ans;
my $reg_match = $Regulation_match+$Positive_regulation_match+$Negative_regulation_match;


#all total
my $all_p = sprintf "%.2f", 100*($Gene_expression_match+$Transcription_match+$Protein_catabolism_match+$Phosphorylation_match+$Localization_match+$Acetylation_match+$Deacetylation_match+$Protein_modification_match+$Ubiquitination_match+$Binding_match+$Regulation_match+$Positive_regulation_match+$Negative_regulation_match)/($Gene_expression_ans+$Transcription_ans+$Protein_catabolism_ans+$Phosphorylation_ans+$Localization_ans+$Acetylation_ans+$Deacetylation_ans+$Protein_modification_ans+$Ubiquitination_ans+$Binding_ans+$Regulation_ans+$Positive_regulation_ans+$Negative_regulation_ans);
my $all_r = sprintf "%.2f", 100*($Gene_expression_match+$Transcription_match+$Protein_catabolism_match+$Phosphorylation_match+$Localization_match+$Acetylation_match+$Deacetylation_match+$Protein_modification_match+$Ubiquitination_match+$Binding_match+$Regulation_match+$Positive_regulation_match+$Negative_regulation_match)/($Gene_expression_gold+$Transcription_gold+$Protein_catabolism_gold+$Phosphorylation_gold+$Localization_gold+$Acetylation_gold+$Deacetylation_gold+$Protein_modification_gold+$Ubiquitination_gold+$Binding_gold+$Regulation_gold+$Positive_regulation_gold+$Negative_regulation_gold);
my $all_f = $all_p + $all_r > 0 ? sprintf "%.2f", 2*$all_p*$all_r/($all_p+$all_r) : "0.00";
my $all_gold = $Gene_expression_gold+$Transcription_gold+$Protein_catabolism_gold+$Phosphorylation_gold+$Localization_gold+$Acetylation_gold+$Deacetylation_gold+$Protein_modification_gold+$Ubiquitination_gold+$Binding_gold+$Regulation_gold+$Positive_regulation_gold+$Negative_regulation_gold;
my $all_ans = $Gene_expression_ans+$Transcription_ans+$Protein_catabolism_ans+$Phosphorylation_ans+$Localization_ans+$Acetylation_ans+$Deacetylation_ans+$Protein_modification_ans+$Ubiquitination_ans+$Binding_ans+$Regulation_ans+$Positive_regulation_ans+$Negative_regulation_ans;
my $all_match = $Gene_expression_match+$Transcription_match+$Protein_catabolism_match+$Phosphorylation_match+$Localization_match+$Acetylation_match+$Deacetylation_match+$Protein_modification_match+$Ubiquitination_match+$Binding_match+$Regulation_match+$Positive_regulation_match+$Negative_regulation_match;

#print P/R/F results
#print "Class:\t\t\t\tPrecision\t\tRecall\t\tF-score\n";
#print "Gene_expression:\t\t$Gene_expression_p\t\t\t$Gene_expression_r\t\t$Gene_expression_f\n";
#print "Transcription:\t\t\t$Transcription_p\t\t\t$Transcription_r\t\t$Transcription_f\n";
#print "Protein_catabolism:\t\t$Protein_catabolism_p\t\t\t$Protein_catabolism_r\t\t$Protein_catabolism_f\n";
#print "Phosphorylation:\t\t$Phosphorylation_p\t\t\t$Phosphorylation_r\t\t$Phosphorylation_f\n";
#print "Localization:\t\t\t$Localization_p\t\t\t$Localization_r\t\t$Localization_f\n";
#print "Binding:\t\t\t$Binding_p\t\t\t$Binding_r\t\t$Binding_f\n";
#print "EVT-TOTAL:\t\t\t$eve_p\t\t\t$eve_r\t\t$eve_f\n";
#print "\n";
#print "Regulation:\t\t\t$Regulation_p\t\t\t$Regulation_r\t\t$Regulation_f\n";
#print "Positive_regulation:\t\t$Positive_regulation_p\t\t\t$Positive_regulation_r\t\t$Positive_regulation_f\n";
#print "Negative_regulation:\t\t$Negative_regulation_p\t\t\t$Negative_regulation_r\t\t$Negative_regulation_f\n";
#print "REG-TOTAL:\t\t\t$reg_p\t\t\t$reg_r\t\t$reg_f\n";
#print "\n";
print "ALL-TOTAL:\t\t\t$all_p\t\t\t$all_r\t\t$all_f\n";
#print "\n\n";
#print detailed results
print "Class:\t\t\t\tGold\t\t\tAnswer\t\tMatch\n";
print "Gene_expression:\t\t$Gene_expression_gold\t\t\t$Gene_expression_ans\t\t$Gene_expression_match\n";
print "Transcription:\t\t\t$Transcription_gold\t\t\t$Transcription_ans\t\t$Transcription_match\n";
print "Protein_catabolism:\t\t$Protein_catabolism_gold\t\t\t$Protein_catabolism_ans\t\t$Protein_catabolism_match\n";
print "Phosphorylation:\t\t$Phosphorylation_gold\t\t\t$Phosphorylation_ans\t\t$Phosphorylation_match\n";
print "Localization:\t\t\t$Localization_gold\t\t\t$Localization_ans\t\t$Localization_match\n";
print "Acetylation:\t\t\t$Acetylation_gold\t\t\t$Acetylation_ans\t\t$Acetylation_match\n";
print "Deacetylation:\t\t\t$Deacetylation_gold\t\t\t$Deacetylation_ans\t\t$Deacetylation_match\n";
print "Protein_modification:\t\t$Protein_modification_gold\t\t\t$Protein_modification_ans\t\t$Protein_modification_match\n";
print "Ubiquitination:\t\t\t$Ubiquitination_gold\t\t\t$Ubiquitination_ans\t\t$Ubiquitination_match\n";
print "Binding:\t\t\t$Binding_gold\t\t\t$Binding_ans\t\t$Binding_match\n";
print "EVT-TOTAL:\t\t\t$eve_gold\t\t\t$eve_ans\t\t$eve_match\n";
print "\n";
print "Regulation:\t\t\t$Regulation_gold\t\t\t$Regulation_ans\t\t$Regulation_match\n";
print "Positive_regulation:\t\t$Positive_regulation_gold\t\t\t$Positive_regulation_ans\t\t$Positive_regulation_match\n";
print "Negative_regulation:\t\t$Negative_regulation_gold\t\t\t$Negative_regulation_ans\t\t$Negative_regulation_match\n";
print "REG-TOTAL:\t\t\t$reg_gold\t\t\t$reg_ans\t\t$reg_match\n";
print "\n";
print "ALL-TOTAL:\t\t\t$all_gold\t\t\t$all_ans\t\t$all_match\n";

close DIR;