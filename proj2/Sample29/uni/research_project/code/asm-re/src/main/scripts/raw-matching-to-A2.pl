#!/usr/bin/perl -w
use Paths::Graph;
$|=1;

$support = "./support";
$test_root = "./test";
$test_orig = $ENV{'TEST'};
die "Environment var 'TEST' is not set correctly" unless $test_orig;

open Z, "$support/multi-word-triggers.txt" or die "cannot open it: $!";
my %multi_triggers;
while (<Z>){
    chomp;
    /^(.+?):\t(.+?)\s*$/;
    $multi_triggers{$1} = $2;
}
close Z;

open Z, "$support/filter-words.txt" or die "cannot open it: $!";
my %filter_words;
while (<Z>){
    chomp;
    /^(.+?):\t(.+?)\s*$/;
    $filter_words{lc($1)} = lc($2);
}
close Z;

open Z, "$support/trigger-all.txt" or die "cannot open it: $!";
my %trigger_all;
while (<Z>){
    chomp;
    /^(.+?)\t(.+?)\s*$/;
    $trigger_all{$1} = $2;
}
close Z;

$matching_dir = "$test_root/matching";
opendir DIR, $matching_dir or die "$!";
foreach my $file (readdir DIR){
    next unless $file =~ /(.*)\.matching$/;
    #next unless $file =~ /(PMC-2065877-13-Materials_and_Methods-04)\.matching$/;
    my $prefix = $1;  print $prefix, "\t", ++$D, "\n";

    open L, "$matching_dir/$file" or die "cannot open the matching file $file: $!";
	my $preds_dir = "$test_root/predictions";
	mkdir $preds_dir unless -d $preds_dir;

    open D, "> $preds_dir/$prefix.a2" or die "cannot open it: $!";  
    
    #read original text
    next if -z "$test_orig/$prefix.txt";
    open Z, "$test_orig/$prefix.txt" or die "cannot open $test_orig/$prefix.txt: $!";
    my $otext;
    while (<Z>){
        $otext .= $_;
    }
    close Z;
    
    #read tokenized sentences
    next if -z "$test_root/pos/$prefix.tps";
    open Z, "$test_root/pos/$prefix.tps" or die "cannot open it: $!";
    my %sentences; $current = 1;
    while (<Z>){
        chomp $_;
        $sentences{$current} = $_;
        $current++;
    }
    close Z;
    
    #read parsed sentences
    next if -z "$test_root/parse/$prefix.dep";
    open Z, "$test_root/parse/$prefix.dep" or die "cannot open it: $!";
    my %parses; my %parse_rep; $current = 1; 
    while (<Z>){
        chomp $_;
        push @{ $parse_rep{$current} }, $_;
        /^.+?\((.+?),\s(.+?)\)$/;
        my $gov = $1; my $dep = $2; 
        $gov =~ /(.+?)-(\d+)\x27*$/; 
        push @{ $parses{$current}{$1} }, $2 if ! grep{$_ eq $2} @{ $parses{$current}{$1} };      
        $dep =~ /(.+?)-(\d+)\x27*$/;
        push @{ $parses{$current}{$1} }, $2 if ! grep{$_ eq $2} @{ $parses{$current}{$1} };  
        if(/^\s*$/){
            foreach my $term (keys %{ $parses{$current} }){
                @{ $parses{$current}{$term} } =
                    sort { $a <=> $b } @{ $parses{$current}{$term} };
                #print "$current\t$term\t@{ $parses{$current}{$term} }", "\n";
            }	
            $current++;
        }
    }
    close Z;

    #read a1 file
    next if -z ".$test_orig/$prefix.a1";
    open Z, "$test_orig/$prefix.a1" or die "cannot open it: $!";
    my %proteins; my %proteins_2; my $last_t; my %proteins_span;
    while (<Z>){
        if(/^(T(\d+))\tProtein\s(\d+)\s(\d+)\t(.+)$/){
            $proteins{$1} = $2;
            $proteins_2{$2} = $5;
            $last_t = $2;
            $proteins_span{$2} = $4;
        }
    }
    close Z;   
   
    my %results;  my $current;  my $event;  my $pattern;  my $rnum;
    while(<L>){
    	next if /^\s*$/; 
    	s/\s+$//;
      if(/Processing sentence \#(\d+)/){ $current = $1; } 
    	if(/Found match\:\s(\d+):/){
    	    $rnum = $1;
    	    /\s*<==\s*/;   
    	    my $lhs = $`;  my $rhs = $'; #'
    	    $lhs =~ s/Found match\:\s*\d*\:\t(.*)/$1/;
    	    $pattern = $1;  $pattern =~ /(\w+)\:?/;  $event = $1;    	    
    	}
    	if(/Nodes matched\:/){  #replace dummy contents in pattern with real contents 
    	    s/Nodes matched\:\s(.*)/$1/;
    	    my @temp = split "; ", $_; 
    	    my %hash;
    	    foreach(@temp){ 
    	        /\s*->\s*/; $hash{$`} = $';#'
    	    }
    	    my @temp2 = $pattern =~ /(.*?:\(.*?\))/g;  my $flag = 0;
    	    foreach my $m (@temp2){ 
    	    	  $m =~ /(.*?):\((.*?)\)/;
    	    	  my $title = $1;  my $content = $2;
    	    	  my @content = split " ", $content;
    	    	  if(scalar @content == 1){
    	            my $f = 1;
    	            foreach my $n (keys %hash){
    	                if( $content =~ /$n/){ $content =~ s/$n/$hash{$n}/; $m = "$title:($content)";  $f = 0; last;}
    	            }
    	            if($f){ $flag = 1; last;}
    	        }
              else{
                  my @temp3;
    	    	      foreach my $o (@content){
    	                foreach my $n (keys %hash){
    	                    if($o =~ /$n/){ $o =~ s/$n/$hash{$n}/; push @temp3, $o; last;}
    	                }
    	            }
    	            if(!@temp3){$flag = 1; last;}
    	            #sort multi-word trigger
    	            my %temp3;  my $subtitle = "";
    	            if($temp3[0] =~ /(.*):(.*)/){$subtitle = $1; $temp3[0] = $2;}
    	            foreach(@temp3){ 
    	                /-(\d+)\x27*\/.*$/;
    	                $temp3{$_} = $1; 
    	            }
    	            my @sort_temp3 = sort {$temp3{$a} <=> $temp3{$b}} keys %temp3;
    	            my $tmp = join " ", @sort_temp3;  
    	            if($subtitle){$m = "$title:($subtitle:$tmp)";}
    	            else{$m = "$title:($tmp)";}
    	        }
    	    }
    	    next if $flag;
    	    my $new_pattern = join " ", @temp2;    	        	    
    	    
#=insert  	      
   	      #check if the pattern should be retained
   	      if(scalar @temp2 > 2){
   	          ${ $results{$current}{$event} }{ $new_pattern }++;	
   	      }
   	      else{
   	      	  my @new_compare = $new_pattern =~ /(.*?:\(.*?\))/g;
   	          $new_compare[0] =~ /(.*?):\((.*?)\)/; my $new_trigger = $2;
   	          $new_compare[1] =~ /(.*?):\((.*?)\)/; my $new_theme = $2;  
   	          my $flag = 1; 	          
   	          foreach my $p (keys %{ $results{$current}{$event} } ) {
   	              my @compare = $p =~ /(.*?:\(.*?\))/g;
   	              next if @compare > 2;
   	              $compare[0] =~ /(.*?):\((.*?)\)/; my $trigger = $2;
   	              $compare[1] =~ /(.*?):\((.*?)\)/; my $theme = $2;
   	              if($theme eq $new_theme){
   	                  $trigger =~ s/(-\d+\x27*)\/-*(\w+|\.)-*$/$1/;	$trigger =~ /^(.*)\-(\d+)\x27*$/; $word = $1; $sn = $2;
   	                  $new_trigger =~ s/(-\d+\x27*)\/-*(\w+|\.)-*$/$1/;	$new_trigger =~ /^(.*)\-(\d+)\x27*$/; $new_word = $1; $new_sn = $2;
   	                  $theme =~ s/(-\d+\x27*)\/-*(\w+|\.)-*$/$1/;	$theme =~ /^(.*)\-(\d+)\x27*$/; $theme_sn = $2;
   	                  if($word eq $new_word){
   	                      if(abs($theme_sn - $sn) < abs($theme_sn - $new_sn)){ $flag = 0; last;}
   	                      else{    	                      	  
   	                          delete $results{$current}{$event}{$p}; 
   	                      }	
   	                  }
   	                  else{
   	                  	
   	                  }
   	              }
   	          }
   	          if($flag){ ${ $results{$current}{$event} }{ $new_pattern }++; }
   	      }
#=cut 	         	       	      
    	    #${ $results{$current}{$event} }{ $new_pattern }++;
    	}    
    }        
    
    # combine regulations events to form individul events
    foreach my $num (keys %results){
        my %regulation_cause;
        #my %regulation_cause_dummy;
        foreach my $eve ( sort keys %{$results{$num}} ){
        	  if($eve =~ /egulation/){
        	      foreach my $pat ( keys %{$results{$num}{$eve}} ){      	      	          	      	  
        	      	  if($pat =~ /^(.+?):\((.+?)\)\s*Cause:\((.+?)\)$/ and $pat !~ /Theme/){
        	              my $type = $1; my $trigger = $2; my $cause = $3; my $flag = 1;
        	              foreach my $existingTrigger(keys %{$regulation_cause{$eve}}){ 
        	              	  if( &compareTrigger($existingTrigger, $trigger) ){       	          
        	                      push @{$regulation_cause{$eve}{$existingTrigger}}, $cause if ! grep{$_ eq $cause} @{$regulation_cause{$eve}{$existingTrigger}}; 
        	                      $flag = 0; #print "@{$regulation_cause{$eve}{$existingTrigger}}\n";
        	                      last;       	          
        	                  }
        	              }
        	              if($flag){
        	                  push @{$regulation_cause{$eve}{$trigger}}, $cause;     	
        	              }
        	          }        	          
        	      }	        	      
            }
        } #foreach my $trigger (keys %regulation_cause){if (scalar @{$regulation_cause{$trigger}} > 2){print "$trigger\t @{$regulation_cause{$trigger}}\n"; exit;}}
   
        foreach my $eve ( sort keys %{$results{$num}} ){        	            	  
        	  if($eve =~ /egulation/){ 
        	      foreach my $pat ( keys %{$results{$num}{$eve}} ){         	      	             	      	     	      	  
        	      	  #if($pat =~ /dummyTrigger/){
        	      	  #    delete $results{$num}{$eve}{$pat};
        	      	  #    next;
        	      	  #}
        	      	  if($pat =~ /^(.+?):\((.+?)\)\s*Cause:\((.+?)\)$/ and $pat !~ /Theme/){
        	      	      delete $results{$num}{$eve}{$pat};
        	      	      next;
        	      	  }
        	      	  next if $pat =~ /Cause:/;
        	          $pat =~ /^(.+?):\((.+?)\)\s*Theme:\((.+?)\)$/;
        	          my $type = $1; my $trigger = $2; my $arg = $3; my $flag = 0;        	                 	          
        	          foreach my $existingTrigger ( keys %{$regulation_cause{$eve}} ){
        	              if( &compareTrigger($existingTrigger, $trigger) ){ 
        	                  foreach my $cause ( @{$regulation_cause{$eve}{$existingTrigger}} ){
        	                      next if $cause eq $arg;
        	                      my @temp;
        	                      push @temp, "$type:($trigger)";
        	                      push @temp, "Theme:($arg)";
        	                      push @temp, "Cause:($cause)";
        	                      my $temp = join " ", @temp;
        	                      $results{$num}{$eve}{$temp} += 1;
        	                      $flag = 1;
        	                  }
        	              }
        	          }
        	          delete $results{$num}{$eve}{$pat} if $flag;        	                  	                  	              	                 	 
        	      }        	      
        	  }           	          	  
        }    
    }
    
    # reverse Regulation to the other two types
    foreach my $num (keys %results){
        foreach my $eve ( sort keys %{$results{$num}} ){
        	  if($eve eq "Regulation"){
        	      foreach my $pat ( keys %{$results{$num}{$eve}} ){
        	          $pat =~ /^(.+?):\((.+?)\)\s*Theme:\((.+?)\)/;
        	          my $trigger = $2;	
        	          $trigger =~ s/(-\d+\x27*)\/-*(\w+|\.)-*(\)?)$/$1$3/; #remove POS tags  # ' = \x27  
        	          foreach(@{$parse_rep{$num}}){
        	              if(/(advmod|amod).*$trigger.*(negatively|negative)/){
        	                  delete $results{$num}{$eve}{$pat};
        	                  $pat =~ s/Regulation:/Negative_regulation:/;
        	                  $results{$num}{Negative_regulation}{$pat}++;        	                  	
        	              }
        	              elsif(/(advmod|amod).*$trigger.*(positively|positive)/){
        	                  delete $results{$num}{$eve}{$pat};
        	                  $pat =~ s/Regulation:/Positive_regulation:/;
        	                  $results{$num}{Positive_regulation}{$pat}++;	
        	              }
        	          }
        	      }
        	  }        	  
        }
    }     
        
    my $T = $last_t+1;  my $E = 1;  my %t_all;  my %e_all;  my $pos_relay = 0;
    
    #process each sentence
    foreach my $num (sort {$a <=> $b} keys %results){
    	#print "Processing $prefix sentence #$num...\n";
        
        my %t;  my %e;  my %events;  my %compare_t;  my %compare_e; #%compare_e for fast comparison purpose
        
        #process non-regulation events
        foreach my $eve ( sort keys %{$results{$num}} ){ 
            next if $eve =~ /egulation/;  
            foreach my $pat ( keys %{$results{$num}{$eve}} ){
            	my @temp = split(/\s+/, $pat);   	
            	foreach(@temp){
            	    if(/BIO_Entity(\d+)-(\d+)\x27*\/NNP/){
            	    	  my $protein = $1 + 1;
            	        s/BIO_Entity(\d+)-(\d+)\x27*\/NNP/T$protein/; #replace BIO with its ID
            	    }
            	    else{ s/(-\d+\x27*)\/-*(\w+|\.)-*(\)?)$/$1$3/; } #remove POS tags  # ' = \x27     	    
            	}
            	$pat = join " ", @temp;
            	my @temp2 = $pat =~ /(.*?:\(.*?\))/g;  $temp2[0] =~ /\((.*?)\)/;  my $trigger = $1;
            	next if $trigger =~ /^T(\d+)$/; #trigger cannot be a protein or an event
            	foreach my $m (@temp2){
                    $m =~ s/^\s*//g;
                    $m =~ s/\s*$//g;
                    $m =~ /(.+):\((.*)\)$/;
                    my $title = $1;  my $content = $2;
                    unless( exists $proteins{$content} ){
                        if( !exists $compare_t{$eve.":".$content} ){
                            $content =~ /^(.*)\-(\d+)\x27*$/;
                            $t{$T} = [$eve, $content, $2];
                            $compare_t{$eve.":".$content} = $T;
                            $m = "$title:(T$T)";
                            $T++;
                        }
                        else{ $m = "$title:(T".$compare_t{$eve.":".$content}.")"; }
                    }
            	}
            	$pat = join " ", @temp2;
            	unless( exists $events{$pat} ){
            	    $events{$pat} = 1;
            	    $e{$E} = $pat;
            	    push @{ $compare_e{$eve.":".$trigger} }, $E;
            	    $E++;
            	}
            }
        }
        
        #process regulation events containing non-regulation events
        #processing rule No.1: Delete regulation events that involve non-regulation events that don't occur
        my @tmp_e;
        foreach my $eve ( sort keys %{$results{$num}} ){ 
            next unless $eve =~ /egulation/;  
            foreach my $pat ( keys %{$results{$num}{$eve}} ){
            	my @temp = split " ", $pat; 
            	my $var = $T;
            	foreach(@temp){ 
            	    if(/BIO_Entity(\d+)-(\d+)\x27*\/NNP/){
            	    	  my $protein = $1 + 1;
            	        s/BIO_Entity(\d+)-(\d+)\x27*\/NNP/T$protein/; #replace BIO with its ID
            	    }
            	    else{ s/(-\d+\x27*)\/-*(\w+|\.)-*(\)?)$/$1$3/; } #remove POS tags  # ' = \x27               	    
            	}
            	$pat = join " ", @temp;
            	my @temp2 = $pat =~ /(.*?:\(.*?\))/g;  $temp2[0] =~ /\((.*?)\)/;  my $trigger = $1;
            	if ($trigger =~ /T(\d+)/){ next; } #trigger cannot be a protein or an event
            	my $flag = 0;  my @tmp = ();  my %equal = (); 
            	foreach my $m (@temp2){
            		    $m =~ s/^\s*//g;
                    $m =~ s/\s*$//g;
                    $m =~ /(.+):\((.*)\)$/;
                    my $title = $1;  my $content = $2;                  
                    unless( exists $proteins{$content} ){                 	
                        if ( !exists $compare_t{$eve.":".$content} and !($content =~ /Binding:|Gene\_expression:|Localization:|Phosphorylation:|Protein\_catabolism:|Transcription:|Negative\_regulation:|Positive\_regulation:|Regulation:/) ){
                            push @tmp, [$T, $eve, $content];
                            $m = "$title:(T$T)";
                            $T++;
                            next;
                        }
                        if ( !exists $compare_e{$content} and $content =~ /Binding:|Gene\_expression:|Localization:|Phosphorylation:|Protein\_catabolism:|Transcription:/ ){                    
                            $flag = 1;  last;
                        }
                        if ( $content =~ /Negative\_regulation:|Positive\_regulation:|Regulation:/ ){ # modifed May 15th. !exists $compare_e{$content} and 
                    	      push @tmp_e, $pat;  $flag = 1;  last;
                        }
                        if ( exists $compare_t{$eve.":".$content} ){                    
                            $m = "$title:(T".$compare_t{$eve.":".$content}.")";
                            next;
                        }
                        if ( exists $compare_e{$content} ){                  
                            my @strings;
                            foreach( @{$compare_e{$content}} ){ push @strings, "E$_"; }
                            my $string = shift @strings;
                            $equal{$string} = \@strings;
                            $m = "$title:($string)";
                            next;
                        }
                    }
            	}
            	if($flag){ $T = $var;  next; }
            	foreach(@tmp){
            	    $_->[2] =~ /^(.*)\-(\d+)\x27*$/;
            	    $t{$_->[0]} = [$_->[1], $_->[2], $2];
            	    $compare_t{$_->[1].":".$_->[2]} = $_->[0];
            	}
            	$pat = join " ", @temp2;            	            	            	            	
            	unless( exists $events{$pat} ){
            	    $events{$pat} = 1;
            	    $e{$E} = $pat;
            	    push @{ $compare_e{$eve.":".$trigger} }, $E;
            	    $E++;
            	}
              if(keys %equal == 1){            	
            	    foreach my $string (keys %equal){
            	        foreach (@{$equal{$string}}){
            	    	      my $temp = $pat; 
            	            $temp =~ s/\($string\)/($_)/g;
            	            unless( exists $events{$temp} ){
            	                $events{$temp} = 1;
            	                $e{$E} = $temp;
            	                push @{ $compare_e{$eve.":".$trigger} }, $E;
            	                $E++;
            	            }
            	        }
            	    }
            	}
            	elsif(keys %equal == 2){   #die"we have a case of 2 subevent arguments here!\n";        	
            	    my @arguments = keys %equal; 
            	    foreach my $string_1 ( ( @{$equal{$arguments[0]}}, $arguments[0] ) ){
            	        my $temp = $pat;
            	        $temp =~ s/\($arguments[0]\)/($string_1)/g; 
            	        foreach my $string_2 ( (@{$equal{$arguments[1]}}, $arguments[1]) ){
            	    	      $temp =~ s/\($arguments[1]\)/($string_2)/g;        	                            	                
            	        }
            	        unless( exists $events{$temp} ){
            	            $events{$temp} = 1;
            	            $e{$E} = $temp;
            	            push @{ $compare_e{$eve.":".$trigger} }, $E;
            	            $E++;
            	        }
            	    }
            	}
            	elsif(keys %equal > 2){die "error here $num:$eve: more than 2 arguments for regulation events!";}
            }
        }               
                
        #process regulation events containing regulation events
        my @iterate;  my $count;  my $number;
        while(1){ $number++; #if($number > 2){die"here";}
            $count = scalar @iterate;
            @iterate = ();
            while(my $pat = shift @tmp_e){#print $pat,"\n";
                my $var = $T;
                my @temp = $pat =~ /(.*?:\(.*?\))/g;  $temp[0] =~ /(.*?):\((.*?)\)/;  my $eve = $1;  my $trigger = $2; 
                if ($trigger =~ /T(\d+)/){ next; } #trigger cannot be a protein or an event
                my $flag = 0;  my $flag_2 = 0;  my @tmp = ();  my %equal =();
                foreach my $m (@temp){
                	  $m =~ s/^\s*//g;
                    $m =~ s/\s*$//g;
                    $m =~ /(.+):\((.*)\)$/;  
                    my $title = $1;  my $content = $2;
                    unless( exists $proteins{$content} ){    
                        if ( exists $compare_t{$eve.":".$content} ){                    
                            $m = "$title:(T".$compare_t{$eve.":".$content}.")";
                            next;
                        }
                        if ( !exists $compare_t{$eve.":".$content} and !($content =~ /Binding:|Gene\_expression:|Localization:|Phosphorylation:|Protein\_catabolism:|Transcription:|Negative\_regulation:|Positive\_regulation:|Regulation:/) ){
                            push @tmp, [$T, $eve, $content];
                            $m = "$title:(T$T)";
                            $T++;
                            next;
                        }
                        if ( !exists $compare_e{$content} and $content =~ /Binding:|Gene\_expression:|Localization:|Phosphorylation:|Protein\_catabolism:|Transcription:/ ){                    
                            $flag_2 = 1;  last;
                        }                                                
                        if ( exists $compare_e{$content} ){                    
                            my @strings;
                            foreach( @{$compare_e{$content}} ){ push @strings, "E$_"; }
                            my $string = shift @strings;
                            $equal{$string} = \@strings;
                            $m = "$title:($string)";
                            next;
                        }
                        if ( !exists $compare_e{$content} and $content =~ /Negative\_regulation:|Positive\_regulation:|Regulation:/ ){
                    	      #die"here: $num:$eve:\n";   
                    	      $flag = 1;  last;
                        }
                    }
                }
                if($flag_2){ $T = $var;  next; }
                if($flag){ $T = $var;  push @iterate, $pat;  next; }
                foreach(@tmp){
                    $_->[2] =~ /^(.*)\-(\d+)\x27*$/;
            	      $t{$_->[0]} = [$_->[1], $_->[2], $2];
            	      $compare_t{$_->[1].":".$_->[2]} = $_->[0];
                }
                $pat = join " ", @temp; 
            	  unless( exists $events{$pat} ){
            	      $events{$pat} = 1;
            	      $e{$E} = $pat;
            	      push @{ $compare_e{$eve.":".$trigger} }, $E;
            	      $E++;
            	  }
                if(keys %equal == 1){            	
            	      foreach my $string (keys %equal){
            	          foreach (@{$equal{$string}}){
            	    	        my $temp = $pat; 
            	              $temp =~ s/\($string\)/($_)/g;
            	              unless( exists $events{$temp} ){
            	                  $events{$temp} = 1;
            	                  $e{$E} = $temp;
            	                  push @{ $compare_e{$eve.":".$trigger} }, $E;
            	                  $E++;
            	              }
            	          }
            	      }
            	  }
            	  elsif(keys %equal == 2){   #die"we have a case of 2 subevent arguments here: $num:$eve:\n";        	
            	      my @arguments = keys %equal; 
            	      foreach my $string_1 ( ( @{$equal{$arguments[0]}}, $arguments[0] ) ){
            	          my $temp = $pat;
            	          $temp =~ s/\($arguments[0]\)/($string_1)/g; 
            	          foreach my $string_2 ( (@{$equal{$arguments[1]}}, $arguments[1]) ){
            	    	        $temp =~ s/\($arguments[1]\)/($string_2)/g;        	                            	                
            	          }
            	          unless( exists $events{$temp} ){
            	              $events{$temp} = 1;
            	              $e{$E} = $temp;
            	              push @{ $compare_e{$eve.":".$trigger} }, $E;
            	              $E++;
            	          }
            	      }
            	  }
            	  elsif(keys %equal > 2){die "error here $num:$eve: more than 2 arguments for regulation events!";}
            }
            @tmp_e = @iterate; #foreach(@tmp_e){print "new: $_\n";}
            if($count == scalar @iterate) { last; }
        }

        #locate indexes of each trigger; identify sentence index first, then inside the sentence       
        my @tokens = split " ", $sentences{$num}; $max_protein = 0;
        foreach my $t (@tokens){
            $t =~ /(.*)\/(.*)$/;  $t = $1;
            if($t =~ /BIO_Entity(\d+)/){
                if($1 >= $max_protein){$max_protein = $1;}	
            }
        }
        $max_protein_span = $proteins_span{$max_protein+1};
        for(my $i = 0; $i < 3; $i++){
            $tokens[$i] = "" unless $tokens[$i];
            $tokens[$i] = $proteins_2{$1+1} if $tokens[$i] =~ /BIO_Entity(\d+)/;           	
            if($tokens[$i] eq "-LSB-"){ $tokens[$i] = "["; }
            if($tokens[$i] eq "-RSB-"){ $tokens[$i] = "]"; }
	          if($tokens[$i] eq "-LRB-"){ $tokens[$i] = "("; }
	          if($tokens[$i] eq "-RRB-"){ $tokens[$i] = ")"; }
        }             
        my @temp = ($tokens[0]." ".$tokens[1]." ".$tokens[2], $tokens[0].$tokens[1]." ".$tokens[2], $tokens[0]." ".$tokens[1].$tokens[2], $tokens[0].$tokens[1].$tokens[2], $tokens[0].". ".$tokens[1]." ".$tokens[2], $tokens[0].".".$tokens[1]." ".$tokens[2], $tokens[0].". ".$tokens[1].$tokens[2], $tokens[0].".".$tokens[1].$tokens[2], $tokens[0]." ".$tokens[1].". ".$tokens[2], $tokens[0].$tokens[1].". ".$tokens[2], $tokens[0]." ".$tokens[1].".".$tokens[2], $tokens[0].$tokens[1].".".$tokens[2], $tokens[0]." ".$tokens[1], $tokens[0].$tokens[1], $tokens[0].".".$tokens[1], $tokens[0].". ".$tokens[1]);
        my $pos;
        foreach(@temp){
            $pos = index($otext, $_, $pos_relay);
            last if $pos != -1;
        } 
        die"cannot find the span for sentence: $prefix:$num\n" if $pos == -1;
        my $pos_save = $pos;
        $pos_relay = $max_protein_span; 
  
        foreach (sort { $t{$a}->[0] cmp $t{$b}->[0] || $t{$a}->[2] <=> $t{$b}->[2] } keys %t){ #print "$t{$_}->[0]\t$t{$_}->[1]\t$t{$_}->[2]\n";            
            my @triggers = split " ", $t{$_}->[1];
            my @tt = split " ", $t{$_}->[1];         
            foreach(@tt){ s/-\d+\x27*$//g; }
            $t{$_}->[1] = join " ", @tt;
  
            if(scalar @triggers == 1){
                $triggers[0] =~ /(.+?)-(\d+)\x27*$/; 
                my $term = $1; my $sn = $2; my $position = 0;
                foreach( @{ $parses{$num}{$term} } ){
                    $position++;
                    if($sn == $_){ last; }	
                }
                my $index_1;
                for(my $i = 0; $i < $position; $i++){
                    $index_1 = index($otext, $term, $pos);
                    #in case of gene match genes, check further the next char is empty
                    my @charset = (";", "\n", ",", ".", " ", ")", "]", ":", "+", "-", '"', "S"); my $flag = 1; 
                    foreach my $char (@charset){
                        if( (substr($otext, $index_1, length($term)+1) eq $term.$char) ){
                            $pos = $index_1 + length($term);
                            $flag = 0;
                            last;
                        }
                    }
                    if($flag){
                        $pos = $index_1 + length($term);
                        redo;	
                    }
                }                                               
                my $index_2 = $index_1 + length($term);
                push @{ $t{$_} }, ($index_1, $index_2);
                $pos = $pos_save;
            }
            else{
            	  my @terms; my @sns;
            	  foreach my $trigger (@triggers){
            	      $trigger =~ /(.+?)-(\d+)\x27*$/; 
                    my $term = $1; my $sn = $2;
                    push @terms, $term;  
                    push @sns, $sn;
                }
                #check if pairwise serial number is consecutive
                my $consecutive = 1;
                for(my $i = 0; $i < scalar @sns - 1; $i++){
                    if ($sns[$i+1] - $sns[$i] != 1){ 
                        $consecutive = 0; 
                        last;
                    }    	
                }
                if($consecutive){
                    my $position = 0;
                    foreach( @{ $parses{$num}{$terms[-1]} } ){
                        $position++;
                        if($sns[-1] == $_){ last; }	
                    }#print "$pos\t@triggers\t$position\n";
                    my $index_1;                    
                    for(my $i = 0; $i < $position; $i++){
                        $index_1 = index($otext, $terms[-1], $pos);                     
                        #in case of gene match genes, check further the next char is empty
                        my @charset = (";", "\n", ",", ".", " ", ")", "]", ":", "+", "-"); my $flag = 1;
                        foreach my $char (@charset){ 
                        	  #if( (substr($otext, $index_1, length($terms[-1])+1) eq $terms[-1].$char) and ( substr($otext, $index_1 - (length(join " ", @terms) - length($terms[-1])), length(join " ", @terms)) eq (join " ", @terms) ) ){
                            if( substr($otext, $index_1, length($terms[-1])+1) eq $terms[-1].$char ){                               
                                $pos = $index_1 + length($terms[-1]);
                                $flag = 0;
                                last;
                            }
                        }
                        if($flag){
                            $pos = $index_1 + length($terms[-1]);
                            redo;	
                        }
                    }                                  
                                                                                           
                    my $index_2 = $index_1 + length($terms[-1]);
                    $index_1 = $index_1 - (length(join " ", @terms) - length($terms[-1]));
                    #print "$num\t$t{$_}->[0]\t@terms\t","$index_1\t$index_2\n";                       
                    if( substr($otext, $index_1, $index_2 - $index_1) eq (join " ", @terms) ){                 
                        push @{ $t{$_} }, ($index_1, $index_2);
                        $pos = $pos_save; 
                    }
                    else {
                        $index_1 = index($otext, (join " ", @terms), $pos);
                        $index_2 = $index_1 + length(join " ", @terms);
                        if( substr($otext, $index_1, $index_2 - $index_1) eq (join " ", @terms) ){                 
                            push @{ $t{$_} }, ($index_1, $index_2);
                            $pos = $pos_save; 
                        }
                        else {die "die here: $num\t$t{$_}->[0]\t@terms\t", substr($otext, $index_1, $index_2 - $index_1), "\t$index_1\t$index_2\n"; } 	
                    }    	
                }
                else{
#=insert                	
                    my $term = $multi_triggers{"@terms"};
                    my $i;
                    for($i = 0; $i < scalar @terms; $i++){
                        last if $terms[$i] eq $term;    	
                    }                    
                    my $sn = $sns[$i]; my $position = 0;
                    foreach( @{ $parses{$num}{$term} } ){
                        $position++;
                        if($sn == $_){ last; }	
                    }
                    my $index_1;
                    for(my $i = 0; $i < $position; $i++){
                        $index_1 = index($otext, $term, $pos);
                        #in case of gene match genes, check further the next char is empty
                        my @charset = (";", "\n", ",", ".", " ", ")", "]", ":", "+", "-"); my $flag = 1;
                        foreach my $char (@charset){
                            if( (substr($otext, $index_1, length($term)+1) eq $term.$char) ){
                                $pos = $index_1 + length($term);
                                $flag = 0;
                                last;
                            }
                        }
                        if($flag){
                            $pos = $index_1 + length($term);
                            redo;	
                        }
                    }                                               
                    my $index_2 = $index_1 + length($term);
                    #print "$num\t$t{$_}->[0]\t@terms\t","$index_1\t$index_2\n"; 
                    push @{ $t{$_} }, ($index_1, $index_2);
                    $pos = $pos_save; 
#=cut                                                           
                }
            }                       
            if( !defined($t{$_}->[3]) or !defined($t{$_}->[4]) ) {
                print "delete trigger: $num\t $_\t @triggers \t $t{$_}->[0] \t $t{$_}->[1]\n";
                delete $t{$_};
            }
        } #foreach(keys %t){print "$num\t $_\t $t{$_}->[0] \t $t{$_}->[1] \t $t{$_}->[2] \t $t{$_}->[3] \t $t{$_}->[4]\n";}
        #foreach(keys %e){print $e{$_},"\n";}
        
        #post-process events and triggers
        foreach my $outer (keys %t){ #remove duplicate and approximately duplicate triggers and fix associated events within same event type
            foreach my $inner (keys %t){    
                next if $inner == $outer;
                if( ( $t{$outer}->[0] eq $t{$inner}->[0] and $t{$outer}->[1] eq $t{$inner}->[1] and $t{$outer}->[3] == $t{$inner}->[3] and $t{$outer}->[4] == $t{$inner}->[4] ) 
                    or ( $t{$outer}->[0] eq $t{$inner}->[0] and index($t{$outer}->[1], $t{$inner}->[1]) != -1   and $t{$outer}->[3] <= $t{$inner}->[3] and $t{$outer}->[4] >= $t{$inner}->[4] ) )
                {                    
                    foreach my $o (keys %e){
                    	$e{$o} =~ s/:\(T$outer\)/:(T$inner)/;
                    	foreach my $i (keys %e){
                            next if $i == $o;
                            if( $e{$o} eq $e{$i} ){ delete $e{$o}; last; }                                 
                        }
                    }
                    delete $t{$outer}; last;
                }
            }
        }        
        foreach my $outer (keys %t){ #remove duplicate and approximately duplicate triggers and fix associated events cross different event types
            foreach my $inner (keys %t){
                next if $inner == $outer;                
                if( $t{$outer}->[0] ne $t{$inner}->[0] and $t{$outer}->[1] ne $t{$inner}->[1] and index($t{$inner}->[1], $t{$outer}->[1]) != -1  and $t{$outer}->[3] >= $t{$inner}->[3] and $t{$outer}->[4] <= $t{$inner}->[4] )
                {   #print "$t{$outer}->[0]\t$t{$outer}->[1]\t$t{$inner}->[0]\t$t{$inner}->[1]\n";                	               	             	  
                	  my $event_num;                
                    foreach my $o (keys %e){
                        if($e{$o} =~ /:\(T$inner\)/){
                            $event_num = $o;
                        }
                    }                    
                    foreach my $o (keys %e){
                        if($e{$o} =~ /:\(T$outer\)/){                            
                            foreach my $k (keys %e){
                                $e{$k} =~ s/:\(E$o\)/:(E$event_num)/;	
                            }
                            delete $e{$o};	
                        }
                    }
                    delete $t{$outer}; last;
                }
            }
        } 
        
        #remove Cause argument of regulation events if Cause argument is theme of the Theme event: Positive_regulation:(T18) Theme:(E10) Cause:(T7)
        foreach my $outer (keys %e){ 
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units < 3;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            next unless $units[1] =~ /(.*?):\(E(.*?)\)/;  my $theme = $2;            
            $units[2] =~ /(.*?):\((.*?)\)/;  my $cause = $2; 
            if($e{$theme} && $e{$theme} =~ /\($cause\)/) {
                $e{$outer} =~ s/Cause.*//; 
                $e{$outer} =~ s/\s*$//;
            }                          
        }
        #Positive_regulation:(T18) Theme:(T7) Cause:(E10): T7 part of E10
        foreach my $outer (keys %e){ 
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units < 3;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            $units[1] =~ /(.*?):\((.*?)\)/;  my $theme = $2;            
            next unless $units[2] =~ /(.*?):\(E(.*?)\)/;  my $cause = $2; 
            if($e{$cause} && $e{$cause} =~ /\($theme\)/) {
                $e{$outer} =~ s/Theme:\($theme\)/Theme:($cause)/;
                $e{$outer} =~ s/Cause.*//; 
                $e{$outer} =~ s/\s*$//;
            }                          
        }   
        #Positive_regulation:(T18) Theme:(E10) Cause:(E10): remove Cause
        foreach my $outer (keys %e){ 
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units < 3;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            $units[1] =~ /(.*?):\((.*?)\)/;  my $theme = $2;            
            $units[2] =~ /(.*?):\((.*?)\)/;  my $cause = $2; 
            if($cause eq $theme) {
                $e{$outer} =~ s/Cause.*//; 
                $e{$outer} =~ s/\s*$//;
            }                          
        }                     
                    
        ##may be for later use:     #processing rule No.2: Delete Regulation events that already occur in the Positive- or Negative- regulation events
        #processing rule No.3: Only a protein or an event can be a Theme or a Cause for regulation events
        #processing rule No.4: Only a protein can be a Theme for non-regulation events
        foreach my $outer (keys %e){
            my $temp = $e{$outer};
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            my $flag = 0;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $eve = $1;  my $trigger = $2;
            #trigger cannot be a protein or an event 
            if ($trigger =~ /E\d+/){delete $e{$outer}; next;} 
            
            foreach my $unit (@units) {
                $unit =~ /(.*?):\((.*?)\)/;  my $name = $1; $content = $2;
                if( $name =~ /Theme|Cause/ and !exists $proteins{$content} and !($content =~ /^E\d+$/) ){
                    delete $e{$outer}; $flag = 1; last;
                }
            }            
        }                       
        
        foreach my $outer (keys %e){ #remove regulation events that share triggers and themes of regulation events that contain Cause
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units > 2;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            $units[1] =~ /(.*?):\((.*?)\)/;  my $theme = $2;
            foreach my $inner (keys %e){
            	  next if $inner == $outer;
            	  my $temp2 = $e{$inner};
                next unless $temp2 =~ /egulation:/;
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                next if scalar @units_2 < 3;
                $units_2[0] =~ /(.*?):\((.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2;
                $units_2[1] =~ /(.*?):\((.*?)\)/;  my $theme_2 = $2;
                $units_2[2] =~ /(.*?):\((.*?)\)/;  my $cause_2 = $2;
                if( ($event eq $event_2) and ($trigger eq $trigger_2) and ($theme eq $theme_2) and $cause_2 ){
                    delete $e{$outer}; 
                    last;  
                }
            }            
        }                 
       
        foreach my $outer (keys %e){ #remove regulation events that use Protein as Theme or Cause, which in fact is the Theme of an Event used in other regulation events
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            $units[1] =~ /(.*?):\((.*?)\)/;  my $theme = $2;
            next if scalar @units >2;
            foreach my $inner (keys %e){ 
            	  next if $inner == $outer;            	 
            	  my $temp2 = $e{$inner};
            	  next unless $temp2 =~ /egulation:/; 
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                next if scalar @units_2 < 3;
                $units_2[0] =~ /(.*?):\((.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2;
                $units_2[1] =~ /(.*?):\((.*?)\)/;  my $theme_2 = $2;
                $units_2[2] =~ /(.*?):\((.*?)\)/;  my $cause_2 = $2;
                if($event eq $event_2 and $trigger eq $trigger_2 and $theme eq $cause_2){
                    #print $e{$outer},"\n";
                    #print $e{$inner},"\n";
                    delete $e{$outer};	
                    last;
                }
            }
        } 
       
#=insert       
        foreach my $outer (keys %e){ #remove regulation events that use Protein as Theme or Cause, which in fact is the Theme of an Event used in other regulation events
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            $units[1] =~ /(.*?):\((T.*?)\)/;  my $theme = $2;
            next if scalar @units >2;
            foreach my $inner (keys %e){ 
            	  next if $inner == $outer;            	 
            	  my $temp2 = $e{$inner};
            	  next unless $temp2 =~ /egulation:/; 
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                next if scalar @units_2 > 2;
                $units_2[0] =~ /(.*?):\((.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2;
                $units_2[1] =~ /(.*?):\(E(.*?)\)/;  my $theme_2 = $2;
                #my $cause_2 = ""; if(scalar @units > 2){$units_2[2] =~ /(.*?):\((T.*?)\)/;  $cause_2 = $2;}
                if($event eq $event_2 and $trigger eq $trigger_2 and exists $e{$theme_2} and ($e{$theme_2} =~ /Gene_expression.*$theme/) ){
                    #print $e{$outer},"\n";
                    #print $e{$inner},"\n";
                    delete $e{$outer};	
                    last;
                }
            }
        } 
#=cut       
        foreach my $outer (keys %e){ #remove duplicate events of special cases of binding events
            my $temp1 = $e{$outer}; 
            next unless $temp1 and $temp1 =~ /^Binding/; 
            my @units1 = $temp1 =~ /(.*?:\(.*?\))/g;
            $units1[0] =~ /(.*?):\((.*?)\)/;  my $event1 = $1; my $trigger1 = $2;
            #unless ($trigger1 =~ /^T/){ delete $e{$outer}; next; }
            my @outer;
            foreach my $unit1 (@units1){
                $unit1 =~ /(.*?):\((.*?)\)/;  my $name1 = $1; $content1 = $2;
                if($name1 =~ /Theme/){ push @outer, $content1; }
            }
            foreach my $inner (keys %e){
            	next if $inner == $outer;
            	my $temp2 = $e{$inner};
            	next unless $temp2 and $temp2 =~ /^Binding/;
            	#if($temp1 eq $temp2){ delete $e{$inner}; next; } 
                my @units2 = $temp2 =~ /(.*?:\(.*?\))/g;
                $units2[0] =~ /(.*?):\((.*?)\)/;  my $event2 = $1; my $trigger2 = $2;
                next unless $event1 eq $event2 and $trigger1 eq $trigger2;
                my @inner;
                foreach my $unit2 (@units2){
                    $unit2 =~ /(.*?):\((.*?)\)/;  my $name2 = $1; $content2 = $2;
                    if(scalar @units1 == scalar @units2){
                        if($name2 =~ /Theme/){ push @inner, $content2 if grep {$_ eq $content2} @outer; }
                    }
                }
                if (scalar @inner == scalar @outer){
                    foreach(keys %e){
                        $e{$_} =~ s/\(E$outer\)/(E$inner)/g;
                    }
                    delete $e{$outer}; last;
                }     
            }
        }                            
                                                                
        foreach my $outer (keys %e){ #remove binding events that share triggers and themes with binding events that contain more Themes
            my $temp = $e{$outer};
            next unless $temp =~ /^Binding:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            shift @units; 
            my @themes;
            foreach my $theme (@units){
                $theme =~ /(.*?):\((.*?)\)/;
                push @themes, $2;	
            }            
            foreach my $inner (keys %e){
            	  next if $inner == $outer;
            	  my $temp2 = $e{$inner};
                next unless $temp2 =~ /^Binding:/;
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                $units_2[0] =~ /(.*?):\((.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2;
                shift @units_2;
                next if scalar @units_2 <= scalar @themes ;
                my @themes_2;
                foreach(@units_2){
                    /(.*?):\((.*?)\)/;  
                    push @themes_2, $2;
                }  
                my $flag = 1;
                foreach my $theme (@themes){
                    if(!grep{$theme eq $_} @themes_2){$flag = 0;}	
                }
                if( ($event eq $event_2) and ($trigger eq $trigger_2) and $flag ){
                    delete $e{$outer};   
                }                
            }            
        }                      
      
        foreach my $outer (keys %e){ #remove events that share themes with other events of same type
            my $temp = $e{$outer};
            #next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            #next if scalar @units > 2;
            $units[0] =~ /(.*?):\(T(.*?)\)/;  my $event = $1; my $trigger = $2; $trigger = lc($t{$trigger}->[1]); 
            $units[1] =~ /(.*?):\((.*?)\)/;  my $theme = $2;
            foreach my $inner (keys %e){
            	  next if $inner == $outer;
            	  my $temp2 = $e{$inner};
                #next unless $temp2 =~ /egulation:/;
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                #next if scalar @units_2 > 2;
                $units_2[0] =~ /(.*?):\(T(.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2; $trigger_2 = lc($t{$trigger_2}->[1]);
                $units_2[1] =~ /(.*?):\((.*?)\)/;  my $theme_2 = $2;
                #$units_2[2] =~ /(.*?):\((.*?)\)/;  my $cause_2 = $2;
                if( ($event eq $event_2) and ($theme eq $theme_2) ){
                    #print $e{$outer},"\n";
                    #print $e{$inner},"\n";
                    if($event ne "Regulation" and $theme =~ /E/ and $trigger =~ /(mediat|requir|lead|led|regulat)/){
                        $e{$outer} =~ s/Theme:\($theme\)/Theme:(E$inner)/;
                        last;
                    }
                    my $flag = 0;
                    foreach my $group (keys %filter_words){
                        if( (join ",", ($trigger, $trigger_2)) eq $group || (join ",", ($trigger_2, $trigger)) eq $group ){
                            #if($trigger eq $filter_words{$group}){ print "delete $e{$inner}\n"; delete $e{$inner}; }
                            if($trigger_2 eq $filter_words{$group}){ 
                                #print "delete $e{$outer}\n"; 
                                delete $e{$outer}; 
                                $flag = 1;
                                last;
                            }
                        }
                    }
                    last if $flag;
                }
            }            
        }         
                         
        foreach my $outer (keys %t){ #remove duplicate triggers cross different event types
            foreach my $inner (keys %t){
                next if $inner == $outer;
                next unless $t{$outer}->[0] =~ /egulation/;
                if( $t{$outer}->[0] ne $t{$inner}->[0] and $t{$outer}->[1] eq $t{$inner}->[1] and $t{$outer}->[3] == $t{$inner}->[3] and $t{$outer}->[4] == $t{$inner}->[4] )
                {   
                	  $t{$outer}->[1] =~ s/-//g; $t{$outer}->[1] =~ s/\s+//g; $t{$inner}->[1] =~ s/-//g; $t{$inner}->[1] =~ s/\s+//g;
                	  if( (exists $trigger_all{$t{$outer}->[1]} and $t{$outer}->[0] ne $trigger_all{$t{$outer}->[1]}) and (exists $trigger_all{$t{$inner}->[1]} and $t{$inner}->[0] eq $trigger_all{$t{$inner}->[1]}) ) {                    
                        delete $t{$outer}; last;
                    }
                }
            }
        }
        
        foreach my $outer (keys %e){ # Neg T59 Theme E5 Cause T8; Neg T59 Theme E6; T8 is in E6; get rid of 2nd Neg
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units > 2;
            $units[0] =~ /(.*?):\((T.*?)\)/;  my $event = $1; my $trigger = $2; 
            next unless $units[1] =~ /(.*?):\(E(.*?)\)/; my $theme = $2;
            foreach my $inner (keys %e){
            	  next if $inner == $outer;
            	  my $temp2 = $e{$inner};
                next unless $temp2 =~ /egulation:/;
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                next if scalar @units_2 < 3;
                $units_2[0] =~ /(.*?):\((T.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2;
                $units_2[1] =~ /(.*?):\((.*?)\)/;  my $theme_2 = $2;
                next unless $units_2[2] =~ /(.*?):\((T.*?)\)/; my $cause_2 = $2;
                if( ($event eq $event_2) and ($trigger eq $trigger_2) and exists $e{$theme} and $e{$theme} =~ /\($cause_2\)/ ){
                    #print $e{$outer},"\n";
                    #print $e{$inner},"\n";
                    delete $e{$outer};
                    last;
                }                
            }
        }                
        
        foreach my $outer (keys %e){ #remove regulation event E6 that: E6	Positive_regulation:T13 Theme:E8; E8	Positive_regulation:T13 Theme:E4
            my $temp = $e{$outer};
            next unless $temp =~ /egulation:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units > 2;
            $units[0] =~ /(.*?):\((.*?)\)/;  my $event = $1; my $trigger = $2;
            $units[1] =~ /(.*?):\((.*?)\)/;  my $theme = $2;
            foreach my $inner (keys %e){
            	next if $inner == $outer;
            	my $temp2 = $e{$inner};
                next unless $temp2 =~ /egulation:/;
                my @units_2 = $temp2 =~ /(.*?:\(.*?\))/g;
                next if scalar @units_2 > 2;
                $units_2[0] =~ /(.*?):\((.*?)\)/;  my $event_2 = $1; my $trigger_2 = $2;
                $units_2[1] =~ /(.*?):\((.*?)\)/;  my $theme_2 = $2; 
                #$units_2[2] =~ /(.*?):\((.*?)\)/;  my $cause_2 = $2;
                if( ($event eq $event_2) and ($trigger eq $trigger_2) and ($theme eq "E$inner")  ){
                    delete $e{$outer}; 
                    last;
                }
            }            
        }                                               
        #####stop here#####
                             
        my $count_2; 
        while(1){ 
        	  local $| = 1; 
            $count_2 = scalar (keys %e);
            
            foreach(keys %t){ #remove triggers that do not appear in any events
                my $trigger = "T$_"; my $flag = 0;
                foreach my $eve (keys %e){
            	      my @temp = $e{$eve} =~ /(.*?:\(.*?\))/g;  $temp[0] =~ /(.*?):\((.*?)\)/;  my $etrigger = $2;
                    if($etrigger eq $trigger){ $flag = 1; last; }   
	              }
	              delete $t{$_} unless $flag;        
            }      
            foreach my $outer (keys %e){ #remove events that involve triggers that have been deleted
                my $temp = $e{$outer}; 
                my @units = $temp =~ /(.*?:\(.*?\))/g;
                foreach my $unit (@units){
                    $unit =~ /(.*?):\((.*?)\)/;  my $name = $1; $content = $2;
                    if($content =~ /T(\d+)$/){
                        if(!exists $t{$1} and !exists $proteins{$content} ){ delete $e{$outer}; }
                    }
                }
            } 
            foreach my $outer (keys %e){ #remove duplicate events
                my $temp = $e{$outer}; 
                foreach my $inner (keys %e){
                    next if $inner == $outer; 
                    my $temp2 = $e{$inner};
                    if($temp2 eq $temp){
                        foreach $o (keys %e){
                            $e{$o} =~ s/:\(E$outer\)/:(E$inner)/;
                        }
                        delete $e{$outer};	
                    }
                }
            }                              
            foreach my $outer(keys %e){ #remove regulation events that involve events that have been deleted 
            	  $e{$outer} =~ s/\s\s/ /;
                my $temp = $e{$outer};
            	  next unless $temp =~ /egulation:/;
                my @units = $temp =~ /(.*?:\(.*?\))/g;
                foreach my $unit (@units){
                    $unit =~ /(.*?):\((.*?)\)/;  my $name = $1; $content = $2;
                    if( $content =~ /^E(\d+)$/ ){
                        if(!exists $e{$1} ){ delete $e{$outer}; last; }
                    }
                }
            }                             
            
            if($count_2 == scalar (keys %e)) { last; }
        } 
        #foreach(keys %t){print "$num\t $_\t $t{$_}->[0] \t $t{$_}->[1] \t $t{$_}->[2] \t $t{$_}->[3] \t $t{$_}->[4]\n";}
        #foreach(keys %e){print $e{$_},"\n";}exit;
        #adding regulation events
        foreach my $outer (keys %e){
            my $temp = $e{$outer};
            next unless $temp =~ /Gene_expression:/;  
            my @units = $temp =~ /(.*?:\(.*?\))/g;
            next if scalar @units > 2;
            $units[0] =~ /(.*?):\(T(.*?)\)/;  my $event = $1; my $trigger = $2; my $trigger_token = lc($t{$trigger}->[1]); 
            if($trigger_token =~ /(overexpression|transfect)/i){
            	  my $flag = 1; my $index;
            	  foreach(keys %t){
            	      if($t{$_}->[0] eq "Positive_regulation" and $t{$_}->[1] eq $t{$trigger}->[1] and $t{$_}->[2] eq $t{$trigger}->[2] and $t{$_}->[3] eq $t{$trigger}->[3]){
            	          $index = $_; $flag = 0; last;	
            	      }
            	  }
                if($flag){
                    $t{$T}->[0] = "Positive_regulation"; $t{$T}->[1] = $t{$trigger}->[1]; $t{$T}->[2] = $t{$trigger}->[2];
                    $t{$T}->[3] = $t{$trigger}->[3]; $t{$T}->[4] = $t{$trigger}->[4];
                    #print "$num\t $T\t $t{$T}->[0] \t $t{$T}->[1] \t $t{$T}->[2] \t $t{$T}->[3] \t $t{$T}->[4]\n";                                  
                    my @temp;
        	          push @temp, "Positive_regulation:(T$T)";
        	          push @temp, "Theme:(E$outer)";
        	          my $temp = join " ", @temp;
                    $e{$E} = $temp;
                    $T++;
                    $E++;
                }
                else{
                    my @temp;
        	          push @temp, "Positive_regulation:(T$index)";
        	          push @temp, "Theme:(E$outer)";
        	          my $temp = join " ", @temp;
                    $e{$E} = $temp;
                    $E++;    	
                }
            }
        }                 
         
        foreach(keys %t){ $t_all{$_} = "$t{$_}->[0] $t{$_}->[3] $t{$_}->[4]\t$t{$_}->[1]"; }
        foreach(keys %e){ $e_all{$_} = $e{$_}; }
    }
    #sort and print results
    my @sort_t = sort {$a <=> $b} keys %t_all;
    my @sort_e = sort {$a <=> $b} keys %e_all;
    foreach(@sort_t){ print D "T$_\t$t_all{$_}\n"; }
    foreach(@sort_e){ $e_all{$_} =~ s/\(//g;  $e_all{$_} =~ s/\)//g;  print D "E$_\t$e_all{$_}\n"; }   
}    
  
sub compareTrigger{
    my @stems_r = split " ", $_[0];
    my @stems_s = split " ", $_[1];
    my (%original, @isect);
    map { $original{$_} = 1 } @stems_r;
    @isect = grep { $original{$_} } @stems_s; 
    return ( scalar @isect ) ? 1 : 0 ;	
}

sub combineLabels {
    my @source = @{ $_[0] };
    my @candidates = @{ $_[1] };
    my $sequence = $_[2];
    if(scalar @source == 0){
        push @candidates, $sequence;	        
    }
    else{
    	  my $current = shift @source;
    	  foreach my $label (@$current){
    	      my @temp = @{$sequence};
    	      push @temp, $label; 
    	      @candidates	= combineLabels( \@source, \@candidates, \@temp );
    	  }
    }
    return @candidates;
}
