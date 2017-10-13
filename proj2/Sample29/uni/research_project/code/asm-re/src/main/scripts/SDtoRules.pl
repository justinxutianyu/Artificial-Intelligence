#!/usr/bin/perl -w

use Paths::Graph;

opendir DIR, "./P+A+P" or die "$!";
my %all_rules;

foreach my $file (readdir DIR){ 
    next unless $file =~ /(.+)\.pap$/;
    #next unless $file =~ /(PMC-1134658-15-Methods-06)\.pap$/;
    my $prefix = $1;

    open F, "./P+A+P/$file" or die "cannot open the file: $!";
    my $new = $prefix.".rule";
    open X, "> ./SD_rules/$new" or die "cannot open $new, $!";

    my (%hash_p, %hash_t, %hash_e);
    my %graph; my %rule_set;

    # reading from file
    while(<F>){
        if(/(.+)\((.*)\,\s(.*)\)/){ # encode parsed tree into an undirected graph
	          my $edge = $1; 
            my $gov = $2;          
            my $dep = $3;
	          push @{ $hash_p{$gov}{$dep} }, $edge;
	          $graph{$gov}{$dep} = 1;
	          $graph{$dep}{$gov} = 1;
	      }
	      elsif(/^T/){ #triggers and entities
	          if(/^(T\d+)\t\w+\s\d+\s\d+\t.*\t(.*)\s*$/){
	              $hash_t{$1} = $2;	
	          }	          
	      }
	      elsif(/^E/){ #events
	          if(/^(.*)\t(.*)\s*$/){
	              $hash_e{$1} = $2;	
	          }
	      }
        elsif (/^\s+$/){
            # process events and generate rules
            foreach(sort keys %hash_e){ 
                if($hash_e{$_} =~ /^(G|T|Pr|L|Ph)/){ #five atomic events
	                  $hash_e{$_} =~ /^(.*?)\:(.*?)\s(.*?)\:(.*?)\s*$/; 
	                  my $type = $1;
		                my $trigger = $2;
		                my $theme = $4;
		                #check
		                $trigger = $hash_t{$trigger} or next; #die "there is no such an entity: $prefix: $hash_e{$_}";
		                $theme = $hash_t{$theme} or next;
		
		                my $rule_L = "$type:($trigger) Theme:($theme)"; #print $rule_L, "\n";
		
		                # Dijkstra's algorithm   #trigger -> theme
		                my @union = (); my @temp = split " ", $trigger;
		                for(my $j=0; $j< scalar @temp; $j++){
                        my $obj = Paths::Graph->new(-origin=>$temp[$j],-destiny=>$theme,-graph=>\%graph);
                        my @paths = $obj->shortest_path();
                        my @pairwise = ();
                        foreach my $path (@paths){ #print join "; ", @$path,"\n";
                        	  my @source = (); my @candidiates = (); my $sequence = [];
			                      for(my $i=0; $i< scalar @$path - 1; $i++){		                          
                                my @position = ();
                                if(exists $hash_p{$path->[$i]}{$path->[$i+1]}){
		                                foreach my $label (@{ $hash_p{$path->[$i]}{$path->[$i+1]} }){    
		                                    my $string = "$label($path->[$i], $path->[$i+1])";
		                                    push @position, $string;
		                                }
		                            }
		                            if(exists $hash_p{$path->[$i+1]}{$path->[$i]}){
			                              foreach my $label (@{ $hash_p{$path->[$i+1]}{$path->[$i]} }){   
			                                  my $string = "$label($path->[$i+1], $path->[$i])";
			                                  push @position, $string;
			                              }
		                            }
		                            push @source, \@position; 
                            } 
                            my @candidates_temp=();                                           
                            @candidates = &combineLabels(\@source, \@candidates_temp, $sequence);
                            push @pairwise, @candidates;
                        }	
                        push @union, \@pairwise;
		                }

		                #combine dependency representations in case of multi-word triggers
		                my @representation = (); my $chain = []; my @representation_temp = ();
		                @representation = &combineSequences(\@union, \@representation_temp, $chain);

		                #generate the set of rules;
		                foreach my $rule (@representation){
		                    my $rule_R = join "; ", @$rule;
		                    print "$prefix:$_ cannot form a dependency path\n" and next if !$rule_R;
		                    push @{$rule_set{$_}}, [$rule_L,$rule_R]; #print "$rule_L\t=>\t$rule_R\n\n";
		                }        		                		
	              }   
	              elsif($hash_e{$_} =~ /^B/){ #binding events
	                  $hash_e{$_} =~ /^(B.*?)\:(.*?)\s(T.*\:.*)+\s*$/;
	                  my $type = $1;
		                my $trigger = $2;
		                my @temp_1 = split /\s/, $3;
		                my %themes;
		                foreach(@temp_1){
		                    /(.*)\:(.*)/;
		                    $themes{$1} = $2;
		                }
		                #check
		                $trigger = $hash_t{$trigger} or next; #die "there is no such an entity: $prefix: $hash_e{$_}";
		                my @temp_2; my @rule_L;
		                foreach my $theme ( sort keys %themes){
		                    $themes{$theme} = $hash_t{$themes{$theme}} or next;
			                  push @temp_2, $themes{$theme};
			                  push @rule_L, "$theme:($themes{$theme})";
		                }
		                next if !@temp_2;
		                unshift @rule_L, "$type:($trigger)"; 
		                my $rule_L = join " ", @rule_L;  #print $rule_L, "\n";
		
		                # Dijkstra's algorithm   #trigger -> theme
		                # three-level recursion	                     
		                my @overall = ();
			              for(my $n=0; $n< scalar @temp_2; $n++){		                
		                    my @union = (); my @temp = split " ", $trigger;
		                    for(my $j=0; $j< scalar @temp; $j++){
                            my $obj = Paths::Graph->new(-origin=>$temp[$j],-destiny=>$temp_2[$n],-graph=>\%graph);
                            my @paths = $obj->shortest_path();
                            my @pairwise = ();
                            foreach my $path (@paths){ #print join "; ", @$path,"\n";
                                my @source = (); my @candidiates = (); my $sequence = [];
			                          for(my $i=0; $i< scalar @$path - 1; $i++){		                          
                                    my @position = ();
                                    if(exists $hash_p{$path->[$i]}{$path->[$i+1]}){
		                                    foreach my $label (@{ $hash_p{$path->[$i]}{$path->[$i+1]} }){    
		                                        my $string = "$label($path->[$i], $path->[$i+1])";
		                                        push @position, $string;
		                                    }
		                                }
		                                if(exists $hash_p{$path->[$i+1]}{$path->[$i]}){
			                                  foreach my $label (@{ $hash_p{$path->[$i+1]}{$path->[$i]} }){   
			                                      my $string = "$label($path->[$i+1], $path->[$i])";
			                                      push @position, $string;
			                                  }
		                                }
		                                #first level recursion
		                                push @source, \@position; 
                                } 
                                my @candidates_temp=();                                           
                                @candidates = &combineLabels(\@source, \@candidates_temp, $sequence);
                                push @pairwise, @candidates;
                            }
                            #second level recursion	
                            push @union, \@pairwise;
		                    }
		                    #combine dependency representations in case of multi-word triggers
		                    my @representation = (); my $chain = []; my @representation_temp = ();
		                    @representation = &combineSequences(\@union, \@representation_temp, $chain);		                         
		                         
		                    #third level recursion
		                    push @overall, \@representation;	                
		                }
		                
		                #combine dependency representations in case that subevent theme is composed of multi-word triggers
		                my @rep = (); my $cha = []; my @rep_temp = ();
		                @rep = &combineSequences(\@overall, \@rep_temp, $cha);	

		                #generate the set of rules;
		                foreach my $rule (@rep){
		                    my $rule_R = join "; ", @$rule;
		                    print "$prefix:$_ cannot form a dependency path\n" and next if !$rule_R;
		                    push @{$rule_set{$_}}, [$rule_L,$rule_R]; #print "$rule_L\t=>\t$rule_R\n\n";
		                }        		         		                		                
	              }
	              elsif($hash_e{$_} =~ /^(R|Po|N)/){ #regulation events
	                  if($hash_e{$_} =~ /^(.*?)\:(.*?)\s(Theme)\:(.*?)\s(Cause)\:(.*?)\s*$/){ #regulation events with cause
	                      my $type = $1; 
		                    my $trigger = $2;
		                    my $theme = $4;
		                    my $cause = $6; 
		                    my $temp; my $temp_theme; my $temp_cause;
		                    #check
		                    next if $theme eq $cause;
		                    $trigger = $hash_t{$trigger} or next; #die "there is no such an entity: $prefix: $hash_e{$_}";			                    	                    
		                    
		                    my @overall_theme = (); 
		                   # separate block 
		                {	
		                    if($hash_t{$theme}){
		                        $theme = $hash_t{$theme};
		                        $temp = $theme;
		                        $temp_theme = $theme;
		                    }
		                    elsif($hash_e{$theme}){
		                        $hash_e{$theme} =~ /^(\w+?)\:(.+?)\s/;
			                      $theme = "$1:$hash_t{$2}"; 
		                        $temp = $hash_t{$2};
		                        $temp_theme = $hash_t{$2};
		                    }
		                    else{print "$prefix: $theme doesn't exist, go to next!\n"; next;}		                    		                    		                    		                    		                   	                    
		
		                     # Dijkstra's algorithm   #trigger -> theme
		                     # three-level recursion	                     
		                     my @temp_theme = split " ", $temp; 
			                   for(my $n=0; $n< scalar @temp_theme; $n++){		                
		                         my @union = (); my @temp = split " ", $trigger;
		                         for(my $j=0; $j< scalar @temp; $j++){
                                 my $obj = Paths::Graph->new(-origin=>$temp[$j],-destiny=>$temp_theme[$n],-graph=>\%graph);
                                 my @paths = $obj->shortest_path();
                                 my @pairwise = ();
                                 foreach my $path (@paths){ #print join "; ", @$path,"\n";
                        	           my @source = (); my @candidiates = (); my $sequence = [];
			                               for(my $i=0; $i< scalar @$path - 1; $i++){		                          
                                         my @position = ();
                                         if(exists $hash_p{$path->[$i]}{$path->[$i+1]}){
		                                         foreach my $label (@{ $hash_p{$path->[$i]}{$path->[$i+1]} }){    
		                                             my $string = "$label($path->[$i], $path->[$i+1])";
		                                             push @position, $string;
		                                         }
		                                     }
		                                     if(exists $hash_p{$path->[$i+1]}{$path->[$i]}){
			                                       foreach my $label (@{ $hash_p{$path->[$i+1]}{$path->[$i]} }){   
			                                           my $string = "$label($path->[$i+1], $path->[$i])";
			                                           push @position, $string;
			                                       }
		                                     }
		                                     #first level recursion
		                                     push @source, \@position; 
                                     } 
                                     my @candidates_temp=();                                           
                                     @candidates = &combineLabels(\@source, \@candidates_temp, $sequence);
                                     push @pairwise, @candidates;
                                 }
                                 #second level recursion	
                                 push @union, \@pairwise;
		                         }
		                         #combine dependency representations in case of multi-word triggers
		                         my @representation = (); my $chain = []; my @representation_temp = ();
		                         @representation = &combineSequences(\@union, \@representation_temp, $chain);		                         
		                         
		                         #third level recusion
		                         push @overall_theme, \@representation;	                
		                     }
		                		                          					
		                  }  # end of separate block
		                 
		                     my @overall_cause = (); 
		                     #separate block  
		                  {  
		                     if($hash_t{$cause}){
		                         $cause = $hash_t{$cause};
		                         $temp = $cause;
		                         $temp_cause = $cause;
		                     }
		                     elsif($hash_e{$cause}){
		                         $hash_e{$cause} =~ /^(\w+?)\:(.+?)\s/;
			                       $cause = "$1:$hash_t{$2}"; 
		                         $temp = $hash_t{$2};
		                         $temp_cause = $hash_t{$2};
		                     }
		                     else{print "$prefix: $cause doesn't exist, go to next!\n"; next;}
		
		                     my $rule_L = "$type:($trigger) Cause:($cause)";   
		                     
		                     # Dijkstra's algorithm   #trigger -> theme
		                     # three-level recursion	                     
		                     my @temp_theme = split " ", $temp; 
			                   for(my $n=0; $n< scalar @temp_theme; $n++){		                
		                         my @union = (); my @temp = split " ", $trigger;
		                         for(my $j=0; $j< scalar @temp; $j++){
                                 my $obj = Paths::Graph->new(-origin=>$temp[$j],-destiny=>$temp_theme[$n],-graph=>\%graph);
                                 my @paths = $obj->shortest_path();
                                 my @pairwise = ();
                                 foreach my $path (@paths){ #print join "; ", @$path,"\n";
                        	           my @source = (); my @candidiates = (); my $sequence = [];
			                               for(my $i=0; $i< scalar @$path - 1; $i++){		                          
                                         my @position = ();
                                         if(exists $hash_p{$path->[$i]}{$path->[$i+1]}){
		                                         foreach my $label (@{ $hash_p{$path->[$i]}{$path->[$i+1]} }){    
		                                             my $string = "$label($path->[$i], $path->[$i+1])";
		                                             push @position, $string;
		                                         }
		                                     }
		                                     if(exists $hash_p{$path->[$i+1]}{$path->[$i]}){
			                                       foreach my $label (@{ $hash_p{$path->[$i+1]}{$path->[$i]} }){   
			                                           my $string = "$label($path->[$i+1], $path->[$i])";
			                                           push @position, $string;
			                                       }
		                                     }
		                                     #first level recursion
		                                     push @source, \@position; 
                                     } 
                                     my @candidates_temp=();                                           
                                     @candidates = &combineLabels(\@source, \@candidates_temp, $sequence);
                                     push @pairwise, @candidates;
                                 }
                                 #second level recursion	
                                 push @union, \@pairwise;
		                         }
		                         #combine dependency representations in case of multi-word triggers
		                         my @representation = (); my $chain = []; my @representation_temp = ();
		                         @representation = &combineSequences(\@union, \@representation_temp, $chain);		                         
		                         
		                         #third level recusion, in case that subevent theme is composed of multi-word triggers
		                         push @overall_cause, \@representation;	                
		                     }
		                		                       		     		                     
		                  }		# end of separate block   
		                  
		                  
		                     my $rule_L = "$type:($trigger) Theme:($theme) Cause:($cause)";  
		                  
		                     #combine dependency representations of theme and cause
		                     my @rep_theme = (); my $cha_theme = []; my @rep_temp_theme = ();
		                     @rep_theme = &combineSequences(\@overall_theme, \@rep_temp_theme, $cha_theme);	
		                     
		                     my @rep_cause = (); my $cha_cause = []; my @rep_temp_cause = ();
		                     @rep_cause = &combineSequences(\@overall_cause, \@rep_temp_cause, $cha_cause);	

		                     #generate the set of rules;
		                     foreach my $rule_theme (@rep_theme){
		                         foreach my $rule_cause (@rep_cause){
		                             my %ultimate;
		                             foreach(@$rule_theme){$ultimate{$_}++;} 
		                             foreach(@$rule_cause){$ultimate{$_}++;}   	
		                           	 my $rule_R = join "; ", (keys %ultimate);
		                           	 print "$prefix:$_ cannot form a dependency path\n" and next if !$rule_R;
		                             push @{$rule_set{$_}}, [$rule_L,$rule_R]; #print "$rule_L\t=>\t$rule_R\n\n";
		                         }		                         
		                     }  		                     		                  
	                  }
		                elsif($hash_e{$_} =~ /^(.*?)\:(.*?)\s(Theme)\:(.*?)\s*$/){ #regulation events without cause
		                    my $type = $1;
		                    my $trigger = $2;
		                    my $theme = $4;
		                    #check
			                  my $temp;
		                    $trigger = $hash_t{$trigger} or next; #die "there is no such an entity: $prefix: $hash_e{$_}";
		                    if($hash_t{$theme}){
		                        $theme = $hash_t{$theme};
		                        $temp = $theme;
		                    }
		                    elsif($hash_e{$theme}){
		                        $hash_e{$theme} =~ /^(\w+?)\:(.+?)\s/;
			                      $theme = "$1:$hash_t{$2}"; 
		                        $temp = $hash_t{$2};
		                    }
		                    else{print "$prefix: $theme doesn't exist, go to next!\n"; next;}
		
		                    my $rule_L = "$type:($trigger) Theme:($theme)";                     
		
		                    # Dijkstra's algorithm   #trigger -> theme
		                    # three-level recursion	                     
		                    my @overall = (); my @temp_theme = split " ", $temp; 
			                  for(my $n=0; $n< scalar @temp_theme; $n++){		                
		                        my @union = (); my @temp = split " ", $trigger;
		                        for(my $j=0; $j< scalar @temp; $j++){
                                my $obj = Paths::Graph->new(-origin=>$temp[$j],-destiny=>$temp_theme[$n],-graph=>\%graph);
                                my @paths = $obj->shortest_path();
                                my @pairwise = ();
                                foreach my $path (@paths){ #print join "; ", @$path,"\n";
                        	          my @source = (); my @candidiates = (); my $sequence = [];
			                              for(my $i=0; $i< scalar @$path - 1; $i++){		                          
                                        my @position = ();
                                        if(exists $hash_p{$path->[$i]}{$path->[$i+1]}){
		                                        foreach my $label (@{ $hash_p{$path->[$i]}{$path->[$i+1]} }){    
		                                            my $string = "$label($path->[$i], $path->[$i+1])";
		                                            push @position, $string;
		                                        }
		                                    }
		                                    if(exists $hash_p{$path->[$i+1]}{$path->[$i]}){
			                                      foreach my $label (@{ $hash_p{$path->[$i+1]}{$path->[$i]} }){   
			                                          my $string = "$label($path->[$i+1], $path->[$i])";
			                                          push @position, $string;
			                                      }
		                                    }
		                                    #first level recursion
		                                    push @source, \@position; 
                                    } 
                                    my @candidates_temp=();                                           
                                    @candidates = &combineLabels(\@source, \@candidates_temp, $sequence);
                                    push @pairwise, @candidates;
                                }
                                #second level recursion	
                                push @union, \@pairwise;
		                        }
		                        #combine dependency representations in case of multi-word triggers
		                        my @representation = (); my $chain = []; my @representation_temp = ();
		                        @representation = &combineSequences(\@union, \@representation_temp, $chain);		                         
		                         
		                        #third level recusion
		                        push @overall, \@representation;	                
		                    }
		                
		                    #combine dependency representations in case that subevent theme is composed of multi-word triggers
		                    my @rep = (); my $cha = []; my @rep_temp = ();
		                    @rep = &combineSequences(\@overall, \@rep_temp, $cha);	

		                    #generate the set of rules;
		                    foreach my $rule (@rep){
		                        my $rule_R = join "; ", @$rule;
		                        print "$prefix:$_ cannot form a dependency path\n" and next if !$rule_R;
		                        push @{$rule_set{$_}}, [$rule_L,$rule_R]; #print "$rule_L\t=>\t$rule_R\n\n";
		                    }        		                												                   
	                  }
	              } 
            }

            # layout rules
            foreach my $event (sort keys %rule_set){
                foreach my $rule ( @{$rule_set{$event}} ){
                    my $represent = $rule->[0]." <== ".$rule->[1];
                    print X $represent;
	                  print X "\n";
	                  $all_rules{$represent} += 1; 
	              }
            }

            %hash_p = (); %hash_t = (); %hash_e = (); %graph = (); %rule_set = ();
            print X "\n";
            next;
        }
    }
}

open Q, ">all_rules" or die "cannot open the file: $!";
my $number; my %hash;
foreach(sort keys %all_rules){
    $number += $all_rules{$_};
    print Q $_, "\n"; 
    /^(\w+):/;
    push @{$hash{$1}}, $_;   
}
close Q;
print $number, "\n";

foreach my $name (keys %hash){
    open F, ">$name" or die "cannot open the file: $!";
    my $n = 1;
    foreach (sort @{$hash{$name}}){print F "$n:\t$_\n"; $n++;} 
    close F;
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

sub combineSequences {
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
    	      my %results;
    	      foreach( (@temp, @$label) ){
    	          $results{$_} += 1;
    	      }
    	      @temp = keys %results;
    	      @candidates	= combineSequences( \@source, \@candidates, \@temp );
    	  }
    }
    return @candidates;
}



