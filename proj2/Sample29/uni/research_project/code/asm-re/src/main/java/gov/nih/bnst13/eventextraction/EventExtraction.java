package gov.nih.bnst13.eventextraction;

import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileReaderUtil;
import edu.ucdenver.ccp.common.file.FileUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst13.patternlearning.EventRule;
import gov.nih.bnst13.patternlearning.RuleParsingException;
import gov.nih.bnst13.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst13.preprocessing.combine.training.CombineInfo;
import gov.nih.bnst13.preprocessing.dp.Edge;
import gov.nih.bnst13.preprocessing.dp.Vertex;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.SortedSet;
import java.util.TreeSet;
import java.util.concurrent.atomic.AtomicInteger;

import org.apache.commons.collections15.OrderedMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tantaman.commons.concurrent.Parallelizer;
import com.tantaman.commons.concurrent.TimeoutParallelizer;


/**	ASM: Approximate Subgraph Matching (ASM) to detect 
 *       approximate subgraph isomorphism between 
 *       dependency graphs of rules and sentences 
 *
 *  @author Haibin Liu
 */

public class EventExtraction {
	private static final Logger LOG = LoggerFactory.getLogger(EventExtraction.class);
	
	/** path to the rule directory */
	private final String rulePath;

	/** the set of rules of simple types excluding PTM event types*/
	private Map<String, List<EventRule>> categorizedSimpleRules;	
	
	/** the set of rules of PTM event types*/
	private Map<String, List<EventRule>> categorizedPTMRules;	
	
	/** the set of rules of complex types */
	private Map<String, List<EventRule>> categorizedComplexRules;
	
	/** the test documents */
	private Map< String, ? extends List<? extends AnnotatedSentence>> documents;
	
	/** store the last protein ID in each document for indexing triggers in later process */
	Map<String, Integer> lastProteinIDOfEachDocument;
	
	/** total event rule count */
	private int totalEventRuleCount = 0;
	
	public static final Map<String, Integer> DEFAULT_THRESHOLDS = new HashMap<String, Integer>(10);
	
	/** the subgraph distance thresholds for each event type */
	private final Map<String, Integer> thresholds = new HashMap<String, Integer>(10); //SUBGRAPH_DISTANCE_THRESHOLD;
	
	/** the weights of the subgraph distance : ws, wl, wd */
	private final static int[] weights = {10, 10, 10};
	
	/**	hash to store all the triggers in rules */
	private Map<String, Set<Vertex>> triggerHash = new HashMap<String, Set<Vertex>>();
	
	/** simple event types */
	String[] simpleEventTypes = {"Gene_expression", "Transcription", "Binding", "Localization", "Protein_catabolism"};
	
	/** PTM event types */
	String[] ptmEventTypes = {"Acetylation", "Deacetylation", "Phosphorylation", "Protein_modification", "Ubiquitination"};

	/** global structure to store eventType->eventRule->impactedDocument relationship for event rule optimization 
	 * (synchronized to allow access concurently by multiple processing thread) */
	Map<String, Map<EventRule, Set<String>>> ruleTypeToRuleToImpactedDocuments = Collections.synchronizedMap(new HashMap<String, Map<EventRule, Set<String>>>());
	
	/** global structure to store document->events relationship for event rule optimization */
	Map<String, List<Set<Event>>> documentToEvents = Collections.synchronizedMap(new HashMap<String, List<Set<Event>>>());

	private String eventPredictionPath;
	
	private int extractionThreads = 1;
	
	private final AtomicInteger docsExtracted = new AtomicInteger(0); // synchronized, so multiple threads can access counter

	private int eventsPanicThreshold = 2000;
	
	/** The maximum number of events allowed for a given rule applied to a given trigger; sets a distance
	 * threshold which cuts off the number of matches at this value as closely as possible, although
	 * all matches with a distance of zero are always included.
	 * 
	 * In the case of ties, increase the threshold to the next highest value only if this takes
	 * us closer to this target value than *not* increasing the threshold
	 *
	 * -1 (the default) is unbounded; any subgraph matches (within the subgraph match tolerance)
	 * will be used
	 */
	private int eventsPerTriggerRuleSoftMax = -1;

	/** the maximum time for event extraction in seconds (-1 for no timeout)
	 * This is enforced by a wrapper which stops waiting for results after a certain time */
	private int extractionHardTimeout = -1;

	/** Whether to timeout internally during event extraction if any class of events takes 
	 * more than 120 seconds (unrelated to extractionHardTimeout) */
	private boolean enableSoftTimeout = true;
	
	private Map<String, Long> extractionTimes = Collections.synchronizedMap(new HashMap<String, Long>());

	private Set<String> blacklistedDocIds;
	
	static {
		DEFAULT_THRESHOLDS.put("Gene_expression", 8); //7, 10
		DEFAULT_THRESHOLDS.put("Transcription", 7); //5, 7
		DEFAULT_THRESHOLDS.put("Protein_catabolism", 10); //10
		DEFAULT_THRESHOLDS.put("Phosphorylation", 8); //7, 10
		DEFAULT_THRESHOLDS.put("Localization", 8); //7, 10
		DEFAULT_THRESHOLDS.put("Acetylation", 3); //3
		DEFAULT_THRESHOLDS.put("Deacetylation", 3); //3
		DEFAULT_THRESHOLDS.put("Protein_modification", 3); //3
		DEFAULT_THRESHOLDS.put("Ubiquitination", 3); //3
		DEFAULT_THRESHOLDS.put("Binding", 7); //7
		DEFAULT_THRESHOLDS.put("Regulation", 3); //3
		DEFAULT_THRESHOLDS.put("Positive_regulation", 3); //3
		DEFAULT_THRESHOLDS.put("Negative_regulation", 3);//3
	}


	/** set the threshold of the number of events in a sentence before we give up */
	public void setEventsPanicThreshold(int newValue) {
		eventsPanicThreshold = newValue;
	}
	
	/** Sets the amount of time allowed for event extraction before timing out */
	public void setExtractionTimeout(int timeout) {
		extractionHardTimeout = timeout;
	}
	
	/**
	 * Constructor to initialize the class fields
	 */
	public EventExtraction(DocumentProducer docColl, String rulePath) {
		this.rulePath = rulePath;
		categorizedSimpleRules = readRuleDirectory("simple");
		categorizedPTMRules = readRuleDirectory("PTM");
		categorizedComplexRules = readRuleDirectory("complex");
		LOG.info("Finished loading rule files with {} event rules ...", totalEventRuleCount );
		this.documents = docColl.getIdsToAnnotatedSentences();
		lastProteinIDOfEachDocument = docColl.getLastProteinIDOfDocuments();
		LOG.info("Finished loading {} testing files ...... ", documents.size());
		initThresholds();
	}
	
	public void disableSoftTimeout() {
		enableSoftTimeout = false;
	}

	protected void initThresholds() {
		thresholds.putAll(DEFAULT_THRESHOLDS);
	}

	public EventExtraction(DocumentProducer docColl, String rulePath, 
			Map<String, Integer> overrideThresholds, int extractionThreads,
			int eventsPerTriggerRuleSoftMax) {
		this(docColl, rulePath);
		for (String threshEvtType : overrideThresholds.keySet()) { // sanity check the user-provided data
			if (!thresholds.containsKey(threshEvtType))
				throw new RuntimeException("Invalid event type for threshold: " + threshEvtType);
		}
		thresholds.putAll(overrideThresholds); //override defaults
		LOG.info("Thresholds in use are: {}", thresholds);
		this.extractionThreads = extractionThreads;
		this.eventsPerTriggerRuleSoftMax = eventsPerTriggerRuleSoftMax;
	}

	public EventExtraction(DocumentProducer docColl, String rulePath, 
			Map<String, Integer> overrideThresholds, int extractionThreads) {
		this(docColl, rulePath, overrideThresholds, extractionThreads, -1);
	}

	public Set<String> docIdsWithLongExtractionTimes(double threshold) {
		Set<String> result = new HashSet<String>();
		for (Map.Entry<String, Long> etEntry : extractionTimes.entrySet()) {
			if (etEntry.getValue() >= threshold)
				result.add(etEntry.getKey());
		}
		return result;
	}
	
	public void removeDocsById(Collection<String> docIds) {
		for (String docId : docIds) {
			if (documents.remove(docId) == null) 
				LOG.error("No document with ID {} exists; not removing", docId);
			else
				LOG.info("Removed document {}", docId);
		}
	}
	
    /**
     * read event rules from the directory where event rules are stored
     */
    private Map<String, List<EventRule> > readRuleDirectory(String type) {	    
    	File directory = new File(rulePath);
	    if ( !directory.isDirectory() ) {
	    	throw new RuntimeException( "The provided diretory: "
				+ rulePath + " is not a directory. Please check." );
	    }
	    Map<String, List<EventRule>> categorizedRules = new HashMap<String, List<EventRule>>();
	    File[] listOfFiles = directory.listFiles();
	    for (File inputFile : listOfFiles) { 
	    	if (! inputFile.isFile() ||! inputFile.getName().matches("^\\S+\\.\\S+$")) 
	    		continue;	    	
			BufferedReader input;
	    	try {
				input = FileReaderUtil.initBufferedReader(inputFile, CharacterEncoding.UTF_8);
			} catch (FileNotFoundException e) {
				throw new RuntimeException("Unable to open the input file: "
						+ inputFile.getName(), e);	
			} 
			if( !inputFile.getName().split("\\.")[1].equals("rule") ) {
				continue;
				//throw new RuntimeException("The rule file name: "
				//		+ inputFile.getName() + " is not valid. Please check.");		
			}
			String category = inputFile.getName().split("\\.")[0]; 
            if(type.equals("simple")) {
            	if(Arrays.asList(simpleEventTypes).contains(category)) {
            	    List<EventRule> rules = readRuleFile(input, category);
    			    categorizedRules.put(category, rules);	
    			    totalEventRuleCount += rules.size();
            	}
            }
            else if (type.equals("PTM")) {
            	if(Arrays.asList(ptmEventTypes).contains(category)) {
            	    List<EventRule> rules = readRuleFile(input, category);			
        			categorizedRules.put(category, rules);	
        			totalEventRuleCount += rules.size();
            	}
            }
            else if (type.equals("complex")) {
            	if(category.endsWith("egulation") ) {
            	    List<EventRule> rules = readRuleFile(input, category);			
        			categorizedRules.put(category, rules);
        			totalEventRuleCount += rules.size();
            	}
            }
	    }
	    
	    //collect category-wise triggers
		for(String category : categorizedRules.keySet()) {
			Set<Vertex> temp = new HashSet<Vertex>();
			Set<String> lemmas = new HashSet<String>();
			for(EventRule rule : categorizedRules.get(category)){
				if(rule.getEventTriggers().size() == 1) { 
					Vertex trigger = new ArrayList<Vertex>(rule.getEventTriggers()).get(0);
					String lemma = trigger.getLemma();
			        if(lemma == null) 
			        	lemma = trigger.getWord().toLowerCase();
			    	if(!lemmas.contains(lemma)) {
			        	temp.add(trigger);
			        	lemmas.add(lemma);
			        }    
				}
			}
			triggerHash.put(category, temp);
		}
		
	    return categorizedRules;
	}
    
    /**
	 * choose the center node in order to keep only one graph node for each annotation
	 * the criteria is based on the Vertex connectivity
	 * @return
	 */
	private Vertex searchCenterNodeForAnnotationGraphNodes(Set<Vertex> graphNodes, DirectedGraph<Vertex, Edge> graph) {
		//directly return the Vertex if the node set only has one node
		if(graphNodes.size() == 1) 
		    return new ArrayList<Vertex>(graphNodes).get(0);
		//sort the graph nodes first from small position to big position
		List<Vertex> sorted = new ArrayList<Vertex>(graphNodes);
		Collections.sort(sorted, new MyComparator()); 
		//System.out.println("before sorting " + graphNodes); System.out.println("after sorting " + sorted);
		Vertex centerNode = null;
		boolean flag = false;
    	for(Vertex v : sorted) {
			Collection<Vertex> neighbors = graph.getNeighbors(v);
			for(Vertex n : neighbors) {
				if(!graphNodes.contains(n))
					flag = true;
			}
			if(flag) { centerNode = v; break; }
		}
    	return centerNode;
	}
	
	/**
	 * 
	 * @param input
	 * @return
	 */
	private static List<EventRule> readRuleFile(BufferedReader input, String category) {
		LOG.info("Reading rules for category {}", category);
		List<EventRule> rules = new ArrayList<EventRule>();
		String line = null;
		try {
			while ((line = input.readLine()) != null) {
				if (line.trim().length() == 0) 
					continue;
				line = line.trim();
				LOG.trace("Reading rule line '{}'", line);
				try {
					EventRule rule = new EventRule(line, category);
					rules.add(rule);
				} catch (RuleParsingException e) {
					LOG.error("Error reading rule line '{}': {}",
						line, e);
				}
			}
			// close input 
			input.close();
		} catch (IOException e) {
			throw new RuntimeException("Unable to process the input file: ", e);
		}
		return rules;
	}
	
	/**
	 * main implementation of event extraction
	 */
	public void eventExtractionByMatchingRulesWithSentences(final String eventPredictionPath) {
		LOG.info("Running event extraction; soft timeouts are {}", enableSoftTimeout ? "ENABLED" : "DISABLED");
		this.eventPredictionPath = eventPredictionPath;
		long starting = System.currentTimeMillis();
		docsExtracted.set(0);
		List<String> docIds = new ArrayList<String>(documents.keySet());
		Collections.sort(docIds);
		Parallelizer par;
		if (extractionHardTimeout == -1)
			par = new Parallelizer(extractionThreads);
		else
			par = new TimeoutParallelizer(extractionThreads, extractionHardTimeout);
		par.forEach(docIds, new Parallelizer.Operation<String>() {
			public void perform(String fileName) {
				try {
					extractForSingleDocument(eventPredictionPath, fileName);
				} catch (Exception e) {
					e.printStackTrace(); // otherwise errors are silently suppressed!!
					System.exit(1);
					throw new RuntimeException(e);
				}
			};
		});
		long ending = System.currentTimeMillis();
		LOG.info("This entire run took " + (ending - starting) + " milliseconds\n");
	}

	protected void extractForSingleDocument(String eventPredictionPath, String fileName) {
//			if (!LOG.isInfoEnabled() && fileCount % 10 == 0) {
//				System.out.println(".");
//				System.out.flush();
//			}
			LOG.debug("Extracting events for '{}'", fileName);
			long startTime = System.currentTimeMillis();
			//no need to proceed further if the document doesn't contain any proteins
			int docIndex = docsExtracted.incrementAndGet();
			if(lastProteinIDOfEachDocument.get(fileName) == null) {
				LOG.trace("No proteins found; returning");
				return;
			}
			//adding output file suffix
	    	File outputFile = new File(eventPredictionPath, fileName + ".a2");
	    	File rawOutputFile = new File(eventPredictionPath, fileName + ".raw");
	    	outputFile.getParentFile().mkdirs();
	    	BufferedWriter output;
	    	BufferedWriter rawOutput;
	    	try {
				output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8, 
						                    WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
				rawOutput = FileWriterUtil.initBufferedWriter(rawOutputFile, CharacterEncoding.UTF_8, 
						                    WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
			} catch (FileNotFoundException e) {
				LOG.error("Problem opening output file: {}", outputFile);
				throw new RuntimeException("Unable to open the output file: " + outputFile.getPath(), e);
			}
	    	LOG.trace("Opened output file {}", outputFile);
			try {
				//no need to proceed further if the document doesn't contain any proteins
				if(lastProteinIDOfEachDocument.get(fileName) == null) {
					output.close();
					rawOutput.close();
					return;
				}
				int triggerStartingID = lastProteinIDOfEachDocument.get(fileName);
				int eventStartingID = 0;
				List<String> documentTriggerList = new ArrayList<String>();
				List<String> documentEventList = new ArrayList<String>();
				List<EventRuleMatch> docRawEventMatches = new ArrayList<EventRuleMatch>();
				int sentenceCount = 0;
				LOG.debug("{} has {} sentences", fileName, documents.get(fileName).size());
				for( AnnotatedSentence sentence : documents.get(fileName) ) {
        			//no need to proceed further if the sentence doesn't contain any proteins
					if(sentence.getProteins() == null) continue;
					LOG.trace("...found proteins in sentence #{}", sentence.getSentenceID());
					//System.out.println("Processing sentence #" + sentence.getSentenceID() + "...");
        			int countSimpleEvents = 0;
        			int countPTMEvents = 0;
        			int countComplexEvents = 0;
        			Set<Event> totalEventSet = new HashSet<Event>(); 
        			Set<Event> simpleEvents = new HashSet<Event>();
        			Set<Event> ptmEvents = new HashSet<Event>();
        			Set<Event> complexEvents = new HashSet<Event>();
				    Map<String, Set<Trigger>> detectedEventTriggers = new HashMap<String, Set<Trigger>>();
				    //three-phrase approach: handle the simple events first
					long simplerulesStart = System.currentTimeMillis();
					simplerules:
				    for( String category : categorizedSimpleRules.keySet() ) {
	        			for( EventRule rule : categorizedSimpleRules.get(category) ) {
							if (enableSoftTimeout && System.currentTimeMillis() - simplerulesStart > 120000) {
								LOG.error("Event extraction (in simple rules) for {} took longer than 120 seconds; giving up", fileName);
								break simplerules;
							}
							LOG.trace("Evaluating simple rule {}", rule);
	        				ASM asm = new ASM(rule, sentence, thresholds.get(category), weights);
	        				long preAsmTime = System.currentTimeMillis();
	        				Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();
	        				long asmTime = System.currentTimeMillis() - preAsmTime;
	        				if (asmTime > 60000 || LOG.isTraceEnabled())
	        					LOG.warn("Took {} ms to find matches using ASM for {}: #{} with rule {}", asmTime,
	        						fileName, sentence.getSentenceID(), rule);
							if (matchings.size() == 0) continue;
	        				LOG.debug("For rule {}:{}, found {} matches", category, rule.getRuleID(), matchings.size());
	        				LOG.trace("  (complete rule: {})", rule);
							//update simpleEvents
							Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(rule, matchings, 
									sentence.getDependencyGraph().getGraph(), rule);
							LOG.trace("From simple rule {} with {} matches, got {} events", rule, matchings.size(), events.size());
							docRawEventMatches.addAll(events);
							for(EventRuleMatch erm : events) {
								Event event = erm.event;
								LOG.trace("Storing event {}", event);
								countSimpleEvents++;
								simpleEvents.add(event);
								//update detectedEventTriggers
								if( !detectedEventTriggers.containsKey(category) ) {
									Set<Trigger> triggers = new HashSet<Trigger>();
									triggers.add(event.getEventTrigger());
									detectedEventTriggers.put(category, triggers);
								}
								else
									detectedEventTriggers.get(category).add(event.getEventTrigger());
							}

					    }
				    }
				    
				    //handle the PTM events second
					long ptmrulesStart = System.currentTimeMillis();
					ptmrules:
				    for( String category : categorizedPTMRules.keySet() ) {
	        			for( EventRule rule : categorizedPTMRules.get(category) ) {
	        				ASM asm = new ASM(rule, sentence, thresholds.get(category), weights);
	        				long preAsmTime = System.currentTimeMillis();
	        				Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();
	        				long asmTime = System.currentTimeMillis() - preAsmTime;
	        				if (asmTime > 60000 || LOG.isTraceEnabled())
	        					LOG.warn("Took {} ms to find matches using ASM for {}: #{} with rule {}", asmTime,
	        						fileName, sentence.getSentenceID(), rule);
	        				if(matchings.size() == 0) continue;
	        				LOG.debug("For rule {}-{}, found {} matches", category, rule.getRuleID(), matchings.size());
							//update ptmEvents
							Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(rule, matchings, 
									sentence.getDependencyGraph().getGraph(), rule);
							docRawEventMatches.addAll(events);
							for(EventRuleMatch erm : events) {
								Event event = erm.event;
								countPTMEvents++;
								ptmEvents.add(event);
								//update detectedEventTriggers
								if( !detectedEventTriggers.containsKey(category) ) {
									Set<Trigger> triggers = new HashSet<Trigger>();
									triggers.add(event.getEventTrigger());
									detectedEventTriggers.put(category, triggers);
								}
								else
									detectedEventTriggers.get(category).add(event.getEventTrigger());
							}
							//perform cross trigger if the rule graph only has one trigger node
							if(rule.getEventTriggers().size() == 1) {
								Vertex ruleTrigger = new ArrayList<Vertex>(rule.getEventTriggers()).get(0);
								for(String type : triggerHash.keySet()) {
									if(Arrays.asList(ptmEventTypes).contains(type)) {
										for(Vertex trigger : triggerHash.get(type)) {
											if(!trigger.getCompareForm().equals(ruleTrigger.getCompareForm()) && 
													!trigger.getGeneralizedPOS().isEmpty() && !ruleTrigger.getGeneralizedPOS().isEmpty() && 
													trigger.getGeneralizedPOS().equals(ruleTrigger.getGeneralizedPOS())) {
												if (enableSoftTimeout && System.currentTimeMillis() - ptmrulesStart > 120000) {
													LOG.error("Event extraction (in PTM rules) for {} took longer than 120 seconds; giving up", fileName);
													break ptmrules;
												}
										        String newRuleString = rule.toString();
										        //change rule category
										        newRuleString = newRuleString.replaceFirst(rule.getEventCategory()+":", type+":");
										        //change rule trigger
										        newRuleString = newRuleString.replaceAll(ruleTrigger.toString(), trigger.toString());
										        EventRule newRule = new EventRule(newRuleString, type); 
										        asm = new ASM(newRule, sentence, thresholds.get(type), weights);
						        				matchings = asm.getApproximateSubgraphMatchingMatches();	
						        				if(matchings.size() == 0) continue;
												//update ptmEvents
												events = getEventsFromMatchingsOfOneRule(newRule, matchings, 
														sentence.getDependencyGraph().getGraph(), rule);
												docRawEventMatches.addAll(events);
												for(EventRuleMatch erm : events) {
													Event event = erm.event;
													countPTMEvents++;
													ptmEvents.add(event);
													//update detectedEventTriggers
													if( !detectedEventTriggers.containsKey(type) ) {
														Set<Trigger> triggers = new HashSet<Trigger>();
														triggers.add(event.getEventTrigger());
														detectedEventTriggers.put(type, triggers);
													}
													else
														detectedEventTriggers.get(type).add(event.getEventTrigger());
												}	
											}
										}
									}
								}
							}
					    }
				    }
				    
				    Set<String> attemptedEventRules = new HashSet<String>();
        			//handle the complex events next using already detected simple events and PTM events
					long complexrulesStart = System.currentTimeMillis();
					complexrules:
        			while(true) {
        				countComplexEvents = 0;
        				for( String category : categorizedComplexRules.keySet() ) {
    	        			for( EventRule rule : categorizedComplexRules.get(category) ) { 
    	        				//if the rule doesn't involve a subevent
    	        				if( !rule.isThemeEvent() && !rule.isCauseEvent() ) {
    	        					if(attemptedEventRules.contains(rule.toString()))
    	        						continue;
    	        					ASM asm = new ASM(rule, sentence, thresholds.get(category), weights);
    		        				long preAsmTime = System.currentTimeMillis();
    		        				Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();
    		        				long asmTime = System.currentTimeMillis() - preAsmTime;
    		        				if (asmTime > 60000 || LOG.isTraceEnabled())
    		        					LOG.warn("Took {} ms to find matches using ASM for {}: #{} with rule {}", asmTime,
    		        						fileName, sentence.getSentenceID(), rule);
        							if(matchings.keySet().size() == 0) continue;
			        				LOG.debug("For category {}, found {} matches", category, matchings.size());
       							//update complexEvents
        							Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(rule, matchings, 
        									sentence.getDependencyGraph().getGraph(), rule);
        							docRawEventMatches.addAll(events);
        							for(EventRuleMatch erm : events) {
        								Event event = erm.event;
        								countComplexEvents++;
        								complexEvents.add(event);
        								//update detectedEventTriggers
    									if( !detectedEventTriggers.containsKey(category) ) {
    										Set<Trigger> triggers = new HashSet<Trigger>();
    										triggers.add(event.getEventTrigger());
    										detectedEventTriggers.put(category, triggers);
    									}
    									else
    										detectedEventTriggers.get(category).add(event.getEventTrigger());
        							}	
        							attemptedEventRules.add(rule.toString());
    	        				}
    	        				//if only theme involves a subevent
    	        				else if (rule.isThemeEvent() && !rule.isCauseEvent()) {
    	        					if(!attemptedEventRules.contains(rule.toString())) {
    	        						ASM asm = new ASM(rule, sentence, thresholds.get(category), weights);
        		        				Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
        		        				if(matchings.keySet().size() == 0) continue;
        								//update complexEvents
        								Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(rule, matchings, 
        										sentence.getDependencyGraph().getGraph(), rule);
        								docRawEventMatches.addAll(events);
        								for(EventRuleMatch erm : events) {
        									Event event = erm.event;
        									countComplexEvents++;
            								complexEvents.add(event);
            								//update detectedEventTriggers
        									if( !detectedEventTriggers.containsKey(category) ) {
        										Set<Trigger> triggers = new HashSet<Trigger>();
        										triggers.add(event.getEventTrigger());
        										detectedEventTriggers.put(category, triggers);
        									}
        									else
        										detectedEventTriggers.get(category).add(event.getEventTrigger());
        								}	
        								attemptedEventRules.add(rule.toString());
    	        					}
    	        					else {
    	        						//perform cross subevent types for the theme
        								Vertex ruleTheme = new ArrayList<Vertex>(rule.getEventThemes()).get(0);
    									for(String type : detectedEventTriggers.keySet()) {
    										List<Trigger> triggerList = new ArrayList<Trigger>(detectedEventTriggers.get(type));
    										for(int i=0; i<triggerList.size(); i++) {
    											Trigger t = triggerList.get(i);
    											Vertex trigger;
    											if(t.getCenterNode() != null)
    												trigger = t.getCenterNode();
    											else {
    												trigger = searchCenterNodeForAnnotationGraphNodes(t.getTriggerNodes(), 
    													sentence.getDependencyGraph().getGraph());
    												t.setCenterNodes(trigger);
    											}
    											//new subevent trigger should not be same as the main trigger
    											boolean isSubEventTriggerSameAsMainTrigger = false;
    											for(Vertex v : rule.getEventTriggers()) {
    												if(v.getCompareForm().equals(trigger.getCompareForm())) {
    													isSubEventTriggerSameAsMainTrigger = true;
    												    break;
    												}    
    											}
    											if(isSubEventTriggerSameAsMainTrigger) continue;
    											if(!trigger.getCompareForm().equals(ruleTheme.getCompareForm()) && 
    													!trigger.getGeneralizedPOS().isEmpty() && !ruleTheme.getGeneralizedPOS().isEmpty() && 
    													trigger.getGeneralizedPOS().equals(ruleTheme.getGeneralizedPOS())) {
    										        String newRuleString = rule.toString();
    										        //change theme category 
    										        newRuleString = newRuleString.replaceFirst("Theme:\\("+rule.getThemeEventCategory()+":", 
    										        		"Theme:("+type+":");
    										        //change theme trigger
    										        newRuleString = newRuleString.replaceAll(ruleTheme.toString(), trigger.toString());
    										        if(attemptedEventRules.contains(newRuleString))
    			    	        						continue;
    										        EventRule newRule = new EventRule(newRuleString, category); 
    										        ASM asm = new ASM(newRule, sentence, thresholds.get(category), weights);
    										        Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
    						        				if(matchings.keySet().size() == 0) continue;
    												//update complexEvents
    						        				Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(newRule, matchings, 
    														sentence.getDependencyGraph().getGraph(), rule);
    												docRawEventMatches.addAll(events);
    												for(EventRuleMatch erm : events) {
    													Event event = erm.event;
    													countComplexEvents++;
    		            								complexEvents.add(event);
    		            								//update detectedEventTriggers
    		        									if( !detectedEventTriggers.containsKey(category) ) {
    		        										Set<Trigger> triggers = new HashSet<Trigger>();
    		        										triggers.add(event.getEventTrigger());
    		        										detectedEventTriggers.put(category, triggers);
    		        									}
    		        									else
    		        										detectedEventTriggers.get(category).add(event.getEventTrigger());
    												}	
    												attemptedEventRules.add(newRuleString);
    											}
    										}
    									}
    	        					}
    	        				}
    	        				//if only cause involves a subevent
    	        				else if (!rule.isThemeEvent() && rule.isCauseEvent()) {
    	        					if(!attemptedEventRules.contains(rule.toString())) {
    	        						ASM asm = new ASM(rule, sentence, thresholds.get(category), weights);
        		        				Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
        		        				if(matchings.keySet().size() == 0) continue;
        								//update complexEvents
        								Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(rule, matchings, 
        										sentence.getDependencyGraph().getGraph(), rule);
        								docRawEventMatches.addAll(events);
        								for(EventRuleMatch erm : events) {
        									Event event = erm.event;
        									countComplexEvents++;
            								complexEvents.add(event);
            								//update detectedEventTriggers
        									if( !detectedEventTriggers.containsKey(category) ) {
        										Set<Trigger> triggers = new HashSet<Trigger>();
        										triggers.add(event.getEventTrigger());
        										detectedEventTriggers.put(category, triggers);
        									}
        									else
        										detectedEventTriggers.get(category).add(event.getEventTrigger());
        								}	
        								attemptedEventRules.add(rule.toString());	
    	        					}
    	        					else {
    	        						//perform cross subevent types for the cause
        								Vertex ruleCause = rule.getEventCause();
    									for(String type : detectedEventTriggers.keySet()) {
    										List<Trigger> triggerList = new ArrayList<Trigger>(detectedEventTriggers.get(type));
    										for(int i=0; i<triggerList.size(); i++) {
    											Trigger t = triggerList.get(i);
    											Vertex trigger;
    											if(t.getCenterNode() != null)
    												trigger = t.getCenterNode();
    											else {
    												trigger = searchCenterNodeForAnnotationGraphNodes(t.getTriggerNodes(), 
    													sentence.getDependencyGraph().getGraph());
    												t.setCenterNodes(trigger);
    											}
    											//new subevent trigger should not be same as the main trigger
    											boolean isSubEventTriggerSameAsMainTrigger = false;
    											for(Vertex v : rule.getEventTriggers()) {
    												if(v.getCompareForm().equals(trigger.getCompareForm())) {
    													isSubEventTriggerSameAsMainTrigger = true;
    												    break;
    												}    
    											}
    											if(isSubEventTriggerSameAsMainTrigger) continue;
    											if(!trigger.getCompareForm().equals(ruleCause.getCompareForm()) && 
    													!trigger.getGeneralizedPOS().isEmpty() && !ruleCause.getGeneralizedPOS().isEmpty() && 
    													trigger.getGeneralizedPOS().equals(ruleCause.getGeneralizedPOS())) {
    										        String newRuleString = rule.toString();
    										        //change cause category 
    										        newRuleString = newRuleString.replaceFirst("Cause:\\("+rule.getCauseEventCategory()+":", 
    										        		"Cause:("+type+":");
    										        //change cause trigger
    										        newRuleString = newRuleString.replaceAll(ruleCause.toString(), trigger.toString());
    										        if(attemptedEventRules.contains(newRuleString))
    			    	        						continue;
    										        EventRule newRule = new EventRule(newRuleString, category); 
    										        ASM asm = new ASM(newRule, sentence, thresholds.get(category), weights);
    										        Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
    						        				if(matchings.keySet().size() == 0) continue;
    												//update complexEvents
    												Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(newRule, matchings, 
    														sentence.getDependencyGraph().getGraph(), rule);
    												docRawEventMatches.addAll(events);
    												for(EventRuleMatch erm : events) {
    													Event event = erm.event;
    													countComplexEvents++;
    		            								complexEvents.add(event);
    		            								//update detectedEventTriggers
    		        									if( !detectedEventTriggers.containsKey(category) ) {
    		        										Set<Trigger> triggers = new HashSet<Trigger>();
    		        										triggers.add(event.getEventTrigger());
    		        										detectedEventTriggers.put(category, triggers);
    		        									}
    		        									else
    		        										detectedEventTriggers.get(category).add(event.getEventTrigger());
    												}	
    												attemptedEventRules.add(newRuleString);
    											}
    										}
    									}	
    	        					}
    	        				}
    	        				//both theme and cause involve a subevent
    	        				else {
    	        					if(!attemptedEventRules.contains(rule.toString())) {
    	        						ASM asm = new ASM(rule, sentence, thresholds.get(category), weights);
        		        				Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
        		        				if(matchings.keySet().size() == 0) continue;
        								//update complexEvents
        								Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(rule, matchings, 
        										sentence.getDependencyGraph().getGraph(), rule);
        								docRawEventMatches.addAll(events);
        								for(EventRuleMatch erm : events) {
        									Event event = erm.event;
        									countComplexEvents++;
            								complexEvents.add(event);
            								//update detectedEventTriggers
        									if( !detectedEventTriggers.containsKey(category) ) {
        										Set<Trigger> triggers = new HashSet<Trigger>();
        										triggers.add(event.getEventTrigger());
        										detectedEventTriggers.put(category, triggers);
        									}
        									else
        										detectedEventTriggers.get(category).add(event.getEventTrigger());
        								}	
        								attemptedEventRules.add(rule.toString());	
    	        					}
    	        					else {
    	        						//perform cross subevent types for both theme and cause simultaneously
        								Vertex ruleTheme = new ArrayList<Vertex>(rule.getEventThemes()).get(0);
        								Vertex ruleCause = rule.getEventCause();
    									for(String typeTheme : detectedEventTriggers.keySet()) {
    										List<Trigger> triggerListTheme = new ArrayList<Trigger>(detectedEventTriggers.get(typeTheme));
    										for(int i=0; i<triggerListTheme.size(); i++) {
    											Trigger t = triggerListTheme.get(i);
    											Vertex triggerTheme;
    											if(t.getCenterNode() != null)
    												triggerTheme = t.getCenterNode();
    											else {
    												triggerTheme = searchCenterNodeForAnnotationGraphNodes(t.getTriggerNodes(), 
    													sentence.getDependencyGraph().getGraph());
    												t.setCenterNodes(triggerTheme);
    											}
    											for(String typeCause : detectedEventTriggers.keySet()) {
    												List<Trigger> triggerListCause = new ArrayList<Trigger>(detectedEventTriggers.get(typeCause));
    												for(int j=0; j<triggerListCause.size(); j++) {	
    													Trigger k = triggerListCause.get(j);
    													Vertex triggerCause;
    													if(k.getCenterNode() != null)
    														triggerCause = k.getCenterNode();
    													else {
    														triggerCause = searchCenterNodeForAnnotationGraphNodes(k.getTriggerNodes(), 
    															sentence.getDependencyGraph().getGraph());
    														k.setCenterNodes(triggerCause);
    													}
    													//triggerTheme and triggerCause cannot be identical
    													if(triggerTheme.equals(triggerCause)) continue;
    													//new subevent trigger should not be same as the main trigger
    													boolean isSubEventTriggerSameAsMainTrigger = false;
    													for(Vertex v : rule.getEventTriggers()) {
    														if(v.getCompareForm().equals(triggerTheme.getCompareForm()) ||
    																v.getCompareForm().equals(triggerCause.getCompareForm())) {
    															isSubEventTriggerSameAsMainTrigger = true;
    														    break;
    														}    
    													}
    													if(isSubEventTriggerSameAsMainTrigger) continue;
    													boolean flag = false; //flag to decide if reverse combination needs to be tried: A B vs. B A
    													if(!( triggerTheme.getCompareForm().equals(ruleTheme.getCompareForm()) &&  
    															triggerCause.getCompareForm().equals(ruleCause.getCompareForm()) )    && 
    															!triggerTheme.getGeneralizedPOS().isEmpty() && !ruleTheme.getGeneralizedPOS().isEmpty() && 
    															triggerTheme.getGeneralizedPOS().equals(ruleTheme.getGeneralizedPOS()) &&
    															!triggerCause.getGeneralizedPOS().isEmpty() && !ruleCause.getGeneralizedPOS().isEmpty() && 
    															triggerCause.getGeneralizedPOS().equals(ruleCause.getGeneralizedPOS()) ) {
    												        String newRuleString = rule.toString();
    												        //change theme category 
    												        newRuleString = newRuleString.replaceFirst("Theme:\\("+rule.getThemeEventCategory()+":", 
    												        		"Theme:("+typeTheme+":");
    												        //change theme trigger
    												        newRuleString = newRuleString.replaceAll(ruleTheme.toString(), triggerTheme.toString());
    												        //change cause category 
    												        newRuleString = newRuleString.replaceFirst("Cause:\\("+rule.getCauseEventCategory()+":", 
    												        		"Cause:("+typeCause+":");
    												        //change cause trigger
    												        newRuleString = newRuleString.replaceAll(ruleCause.toString(), triggerCause.toString());
    												        if(attemptedEventRules.contains(newRuleString))
    					    	        						continue;
    												        EventRule newRule = new EventRule(newRuleString, category); 
    												        ASM asm = new ASM(newRule, sentence, thresholds.get(category), weights);
    												        Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
    								        				if(matchings.keySet().size() == 0) continue;
    														//update complexEvents
    														Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(newRule, matchings, 
    																sentence.getDependencyGraph().getGraph(), rule);
    														docRawEventMatches.addAll(events);
    														flag = true;
    														for(EventRuleMatch erm : events) {
    															Event event = erm.event;
    															countComplexEvents++;
    				            								complexEvents.add(event);
    				            								//update detectedEventTriggers
    				        									if( !detectedEventTriggers.containsKey(category) ) {
    				        										Set<Trigger> triggers = new HashSet<Trigger>();
    				        										triggers.add(event.getEventTrigger());
    				        										detectedEventTriggers.put(category, triggers);
    				        									}
    				        									else
    				        										detectedEventTriggers.get(category).add(event.getEventTrigger());
    														}	
    														attemptedEventRules.add(newRuleString);
    													}
    													if(!flag && !( triggerCause.getCompareForm().equals(ruleTheme.getCompareForm()) &&  
    															triggerTheme.getCompareForm().equals(ruleCause.getCompareForm()) )    && 
    															!triggerCause.getGeneralizedPOS().isEmpty() && !ruleTheme.getGeneralizedPOS().isEmpty() && 
    															triggerCause.getGeneralizedPOS().equals(ruleTheme.getGeneralizedPOS()) &&
    															!triggerTheme.getGeneralizedPOS().isEmpty() && !ruleCause.getGeneralizedPOS().isEmpty() && 
    															triggerTheme.getGeneralizedPOS().equals(ruleCause.getGeneralizedPOS()) ) {
    														String newRuleString = rule.toString();
    												        //change theme category 
    												        newRuleString = newRuleString.replaceFirst("Theme:\\("+rule.getCauseEventCategory()+":", 
    												        		"Theme:("+typeCause+":");
    												        //change theme trigger
    												        newRuleString = newRuleString.replaceAll(ruleTheme.toString(), triggerCause.toString());
    												        //change cause category 
    												        newRuleString = newRuleString.replaceFirst("Cause:\\("+rule.getThemeEventCategory()+":", 
    												        		"Cause:("+typeTheme+":");
    												        //change cause trigger
    												        newRuleString = newRuleString.replaceAll(ruleCause.toString(), triggerTheme.toString());
    												        if(attemptedEventRules.contains(newRuleString))
    					    	        						continue;
    												        EventRule newRule = new EventRule(newRuleString, category); 
    												        ASM asm = new ASM(newRule, sentence, thresholds.get(category), weights);
    												        Map<Double, List< Map<Vertex, Vertex>>> matchings = asm.getApproximateSubgraphMatchingMatches();	
    								        				if(matchings.keySet().size() == 0) continue;
    														//update complexEvents
    														Set<EventRuleMatch> events = getEventsFromMatchingsOfOneRule(newRule, matchings, 
    																sentence.getDependencyGraph().getGraph(), rule);
    														docRawEventMatches.addAll(events);
    														for(EventRuleMatch erm : events) {
    															Event event = erm.event;
    															countComplexEvents++;
    				            								complexEvents.add(event);
    				            								//update detectedEventTriggers
    				        									if( !detectedEventTriggers.containsKey(category) ) {
    				        										Set<Trigger> triggers = new HashSet<Trigger>();
    				        										triggers.add(event.getEventTrigger());
    				        										detectedEventTriggers.put(category, triggers);
    				        									}
    				        									else
    				        										detectedEventTriggers.get(category).add(event.getEventTrigger());
    														}	
    														attemptedEventRules.add(newRuleString);	
    													}
    												}
    											}
    										}
    									}	
    	        					}
    	        				}
    	        			}

							if (enableSoftTimeout && System.currentTimeMillis() - complexrulesStart > 120000) {
								LOG.error("Event extraction (in complex rules) for {} took longer than 120 seconds; giving up", fileName);
								break complexrules;
							}

            			} 
        				if(countComplexEvents == 0) {
        					break;
        				}	

        			} // end while(true) loop
        			//System.out.println(simpleEvents.size() + " " + ptmEvents.size() + " " + complexEvents.size());
        			totalEventSet.addAll(simpleEvents); totalEventSet.addAll(ptmEvents); totalEventSet.addAll(complexEvents);
        			//populate the two global structure for rule optimization use
        			LOG.debug("Found {} events in document {}", totalEventSet.size(), fileName);
        			for(Event event : totalEventSet) {
        				LOG.trace("found event {}", event);
        			    if(ruleTypeToRuleToImpactedDocuments.containsKey(event.getOriginalEventRule().getEventCategory())) {
        			        if(ruleTypeToRuleToImpactedDocuments.get(event.getOriginalEventRule().getEventCategory()).
        			        		containsKey(event.getOriginalEventRule())) {
        			        	ruleTypeToRuleToImpactedDocuments.get(event.getOriginalEventRule().getEventCategory()).
    			        		get(event.getOriginalEventRule()).add(fileName);	
        			        }
        			        else {
        			        	Set<String> impactedDocuments = new HashSet<String>();
            			    	impactedDocuments.add(fileName);
        			        	ruleTypeToRuleToImpactedDocuments.get(event.getOriginalEventRule().getEventCategory()).
        			        	put(event.getOriginalEventRule(), impactedDocuments);
        			        }
        			    }
        			    else {
        			    	Map<EventRule, Set<String>> ruleToImpactedDocuments = new HashMap<EventRule, Set<String>>();
        			    	Set<String> impactedDocuments = new HashSet<String>();
        			    	impactedDocuments.add(fileName);
        			    	ruleToImpactedDocuments.put(event.getOriginalEventRule(), impactedDocuments);
        			    	ruleTypeToRuleToImpactedDocuments.put(event.getOriginalEventRule().getEventCategory(), ruleToImpactedDocuments);
        			    }
        			}
        			if(documentToEvents.containsKey(fileName))
        				documentToEvents.get(fileName).add(totalEventSet);
        			else {
        				List<Set<Event>> list = new ArrayList<Set<Event>>();
        				list.add(totalEventSet);
        				documentToEvents.put(fileName, list);
        			}	
        			//postprocess raw events
				    if(!totalEventSet.isEmpty()) 
				    	totalEventSet = postprocessRawExtractedEvents(totalEventSet);
				    //convert postprocessed raw events to A2 format
        			LOG.debug("({} events after post-processing)", totalEventSet.size());
				    if(!totalEventSet.isEmpty()) {
				    	Integer[] currentIDs = rawEventsToA2Strings(totalEventSet, triggerStartingID, eventStartingID, 
				    			documentTriggerList, documentEventList); 
				    	triggerStartingID = currentIDs[0];
				    	eventStartingID = currentIDs[1];
				    }
        			//rule optimization needs eventrule->document and document->events mapping
				    LOG.trace("Finished processing sentence #{}", sentence.getSentenceID());
				} // end processing one sentence
				//print event results
				LOG.debug("Found {} triggers and {} events for document", 
						documentTriggerList.size(), documentEventList.size());
			    for(String trigger : documentTriggerList) {
			    	//System.out.println(trigger);
			    	output.write(trigger + "\n");
			    }
			    for(String event : documentEventList) {
			    	//System.out.println(event);
			    	output.write(event + "\n");
			    } 
				for (EventRuleMatch erm : docRawEventMatches) 
					rawOutput.write(erm + "\n");
				rawOutput.close();
				output.close();	
				long endTime = System.currentTimeMillis();
				extractionTimes.put(fileName, endTime - startTime);
				LOG.info("Extracting {} events from '{}' ({} of {}) took {} ms", 
						documentEventList.size(), fileName, 
						docIndex, documents.size(), endTime - startTime);
			} catch (IOException e) {
				throw new RuntimeException("Unable to process the output file: ", e);
			} 
	}
	
	/**
	 * convert raw graph matching event extraction results into shared task A2 format
	 * @param totalEventSet
	 * @param triggerID
	 * @param eventID
	 * @param triggerList
	 * @param eventList
	 * @return
	 */
	public Integer[] rawEventsToA2Strings(Set<Event> totalEventSet, int triggerID, int eventID, List<String> triggerList, List<String> eventList) {
		int triggerStartingID = triggerID;
		int eventStartingID = eventID;
		Map<String, Integer> detectedTriggers = new HashMap<String, Integer>();
		Set<String> detectedEvents = new HashSet<String>();
		//handle trigger first
		Map<String, Map<Trigger, Integer>> triggers= new HashMap<String, Map<Trigger, Integer>>();
		for(Event event : totalEventSet) {
			if(triggers.containsKey(event.getEventCategory()))
				triggers.get(event.getEventCategory()).put(event.getEventTrigger(), 1);
			else {
				Map<Trigger, Integer> set = new HashMap<Trigger, Integer>();
				set.put(event.getEventTrigger(), 1);
				triggers.put(event.getEventCategory(), set);
			}
		}
		for(String category : triggers.keySet()) {
			for(Trigger trigger : triggers.get(category).keySet()) {
				if(trigger.getTriggerNodes().size() == 1) {
		    	    Vertex triggerNode = new ArrayList<Vertex>(trigger.getTriggerNodes()).get(0);
		    	    trigger.setTriggerRecord(category + " " + 
		    				triggerNode.getOffset() + " " + (triggerNode.getOffset() + triggerNode.getWord().length()) + "\t" + triggerNode.getWord());   
		    	}
		    	else {
		    		List<Vertex> sorted = new ArrayList<Vertex>(trigger.getTriggerNodes());
		    		Collections.sort(sorted, new MyNewComparator());
		    		Vertex vStart = sorted.get(0);
		    		Vertex vEnd = sorted.get(sorted.size()-1);
		    		if(vEnd.getTokenPosition() - vStart.getTokenPosition() + 1 == trigger.getTriggerNodes().size()) {
		    			List<String> list = new ArrayList<String>();
		    			for(Vertex v : sorted)
		    				list.add(v.getWord());
		    			trigger.setTriggerRecord(category + " " + 
			    				 vStart.getOffset() + " " + ( vEnd.getOffset() +  vEnd.getWord().length()) + "\t" + 
			    				 CombineInfo.join(list, " "));	
		    		}
		    		else {
		    			trigger.setTriggerRecord(category + " " + 
			    				 vEnd.getOffset() + " " + ( vEnd.getOffset() +  vEnd.getWord().length()) + "\t" + vEnd.getWord());	
		    		}
		    	}
				if(!detectedTriggers.containsKey(trigger.toA2String())) {
					triggers.get(category).put(trigger, ++triggerStartingID);
					triggerList.add("T" + triggerStartingID + "\t" + trigger.toA2String());
					trigger.setTriggerID(triggerStartingID);
					detectedTriggers.put(trigger.toA2String(), triggerStartingID);
				}
				else{
					triggers.get(category).put(trigger, detectedTriggers.get(trigger.toA2String()));
					trigger.setTriggerID(detectedTriggers.get(trigger.toA2String()));
				}
			}
		}
		//handle event next  
		//simple events
		for(Event event : totalEventSet) {
			if(!event.getEventCategory().endsWith("egulation")) { 
				StringBuilder sb = new StringBuilder(); 
				sb.append("E" + ++eventStartingID + "\t");
        		event.setEventID(eventStartingID);
		    	sb.append(event.getEventCategory());
				sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
				if(event.getEventThemes().size() > 1) {
			    	List<Vertex> sorted = new ArrayList<Vertex>(event.getEventThemes());
		    		Collections.sort(sorted, new MyNewComparator());	
		    		sb.append("Theme:" + sorted.get(0).getProteinID() + " ");
					for(int i=1; i<sorted.size(); i++) {
						sb.append("Theme" + (i+1) + ":" + sorted.get(i).getProteinID() + " ");
					}
			    }
			    else {
			    	sb.append("Theme:" + new ArrayList<Vertex>(event.getEventThemes()).get(0).getProteinID());
			    	if(event.hasCause()) {
			    		sb.append(" Cause:" + event.getEventCause().getProteinID());
			    	}
			    } 
				eventList.add(sb.toString());
			}
		}
		//regulation events
		int preRegEventCount = eventList.size();
        while(true) {
        	int previousEventCount = eventList.size();
        	for(Event event : totalEventSet) {
    			if(event.getEventCategory().endsWith("egulation") && event.getEventID() == -1 ) {
    			    //no cause argument
    				if(!event.hasCause()) {
    			        //theme is a subevet
    					if(event.isThemeEvent()) {
    			        	Vertex theme = event.getThemeEvent();
    			        	List<Event>	subevents = searchForSubevents(event, theme, event.getThemeEventCategory(), totalEventSet);
    			        	boolean flag = true;
    			        	for(Event e : subevents) {
    			        		if(e.getEventID() == -1 ) {
    				        		flag = false;
    				        		break;
    				        	}	
    			        	}
    			        	if(!flag || subevents.isEmpty()) continue;
    			        	for(Event e : subevents) {
    			        		if(e.getAssociatedEventIDs().isEmpty())
    			        			e.getAssociatedEventIDs().add(e.getEventID());
    			        		for(Integer id : e.getAssociatedEventIDs()) {
    			        			StringBuilder sb = new StringBuilder();
    						    	sb.append(event.getEventCategory());
    								sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
    								sb.append("Theme:E" + id );
    								if(!detectedEvents.contains(sb.toString())) { 
    									eventList.add("E" + ++eventStartingID + "\t" + sb.toString());	
    									if(event.getEventID() == -1) 
        				        			event.setEventID(eventStartingID);
    									event.getAssociatedEventIDs().add(eventStartingID);
    									detectedEvents.add(sb.toString());
    								}
    			        		}	
    			        	}
    			        }
    					//theme is a protein
    			        else {
    			        	StringBuilder sb = new StringBuilder();
    			        	sb.append("E" + ++eventStartingID + "\t");
    		        		event.setEventID(eventStartingID);
    				    	sb.append(event.getEventCategory());
    						sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
    						sb.append("Theme:" + new ArrayList<Vertex>(event.getEventThemes()).get(0).getProteinID() );
    						eventList.add(sb.toString());
    			        }
    			    }
    				//with cause argument
    			    else {
    			    	//theme is a subevent but cause is a protein
                        if(event.isThemeEvent() && !event.isCauseEvent()) {
                        	Vertex theme = event.getThemeEvent();
    			        	List<Event>	subevents = searchForSubevents(event, theme, event.getThemeEventCategory(), totalEventSet);
    			        	boolean flag = true;
    			        	for(Event e : subevents) {
    			        		if(e.getEventID() == -1 ) {
    				        		flag = false;
    				        		break;
    				        	}	
    			        	}
    			        	if(!flag || subevents.isEmpty()) continue;
    			        	for(Event e : subevents) {
    			        		if(e.getAssociatedEventIDs().isEmpty())
    			        			e.getAssociatedEventIDs().add(e.getEventID());
    			        		for(Integer id : e.getAssociatedEventIDs()) {
    			        			StringBuilder sb = new StringBuilder();
    						    	sb.append(event.getEventCategory());
    								sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
    								sb.append("Theme:E" + id );
    								sb.append(" Cause:" + event.getEventCause().getProteinID());
    								if(!detectedEvents.contains(sb.toString())) { 
    									eventList.add("E" + ++eventStartingID + "\t" + sb.toString());	
    									if(event.getEventID() == -1) 
        				        			event.setEventID(eventStartingID);
    									event.getAssociatedEventIDs().add(eventStartingID);
    									detectedEvents.add(sb.toString());
    								}		
    			        		}	
    			        	}
    			    	}
                        //theme is a protein but cause is a subevent
                        else if(!event.isThemeEvent() && event.isCauseEvent()) {
                        	Vertex cause = event.getCauseEvent();
    			        	List<Event>	subevents = searchForSubevents(event, cause, event.getCauseEventCategory(), totalEventSet);
    			        	boolean flag = true;
    			        	for(Event e : subevents) {
    			        		if(e.getEventID() == -1 ) {
    				        		flag = false;
    				        		break;
    				        	}	
    			        	}
    			        	if(!flag || subevents.isEmpty()) continue;
    			        	for(Event e : subevents) {
    			        		if(e.getAssociatedEventIDs().isEmpty())
    			        			e.getAssociatedEventIDs().add(e.getEventID());
    			        		for(Integer id : e.getAssociatedEventIDs()) {
    			        			StringBuilder sb = new StringBuilder();
    						    	sb.append(event.getEventCategory());
    								sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
    								sb.append("Theme:" + new ArrayList<Vertex>(event.getEventThemes()).get(0).getProteinID() + " ");
    								sb.append("Cause:E" + id );
    								if(!detectedEvents.contains(sb.toString())) { 
    									eventList.add("E" + ++eventStartingID + "\t" + sb.toString());	
    									if(event.getEventID() == -1) 
        				        			event.setEventID(eventStartingID);
    									event.getAssociatedEventIDs().add(eventStartingID);
    									detectedEvents.add(sb.toString());
    								}	
    			        		}	
    			        	}
    			    	}
                        //both theme and cause are subevents
                        else if(event.isThemeEvent() && event.isCauseEvent()) {
                        	Vertex theme = event.getThemeEvent();
    			        	List<Event>	subeventsTheme = searchForSubevents(event, theme, event.getThemeEventCategory(), totalEventSet);
    			        	boolean flag = true;
    			        	for(Event e : subeventsTheme) {
    			        		if(e.getEventID() == -1 ) {
    				        		flag = false;
    				        		break;
    				        	}	
    			        	}
    			        	if(!flag || subeventsTheme.isEmpty()) continue;
    			        	Vertex cause = event.getCauseEvent();
    			        	List<Event>	subeventsCause = searchForSubevents(event, cause, event.getCauseEventCategory(), totalEventSet);
    			        	flag = true;
    			        	for(Event e : subeventsCause) {
    			        		if(e.getEventID() == -1 ) {
    				        		flag = false;
    				        		break;
    				        	}	
    			        	}
    			        	if(!flag || subeventsCause.isEmpty()) continue;
    			        	for(Event e : subeventsTheme) {
    			        		if(e.getAssociatedEventIDs().isEmpty())
    			        			e.getAssociatedEventIDs().add(e.getEventID());
    			        		for(Integer id : e.getAssociatedEventIDs()) {
    								for(Event k : subeventsCause) {
    					        		if(k.getAssociatedEventIDs().isEmpty())
    					        			k.getAssociatedEventIDs().add(k.getEventID());
    					        		for(Integer kid : k.getAssociatedEventIDs()) {
    					        			StringBuilder sb = new StringBuilder();
    	    						    	sb.append(event.getEventCategory());
    	    								sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
    	    								sb.append("Theme:E" + id );
    					        			sb.append(" Cause:E" + kid );
    					        			if(!detectedEvents.contains(sb.toString())) { 
    	    									eventList.add("E" + ++eventStartingID + "\t" + sb.toString());	
    	    									if(event.getEventID() == -1) 
    	        				        			event.setEventID(eventStartingID);
    	    									event.getAssociatedEventIDs().add(eventStartingID);
    	    									detectedEvents.add(sb.toString());
    	    								}			
    					        		}	
    					        	}
    			        		}	
    			        	}
    			    	}   
                        //both theme and cause are proteins
    			    	else {
    			    		StringBuilder sb = new StringBuilder();
    						sb.append("E" + ++eventStartingID + "\t");
    						event.setEventID(eventStartingID);
    				    	sb.append(event.getEventCategory());
    						sb.append(":T" + triggers.get(event.getEventCategory()).get(event.getEventTrigger()) + " ");
    						sb.append("Theme:" + new ArrayList<Vertex>(event.getEventThemes()).get(0).getProteinID() + " ");
    						sb.append(" Cause:" + event.getEventCause().getProteinID());
    						eventList.add(sb.toString());
    			    	}
    			    }
    			}
    		}
        	/*
        	for(Event event : totalEventSet) {
    			if(event.getEventCategory().endsWith("egulation") && event.getEventID() == -1 ) {
    				//System.out.println("Problem " + event);
    			}
        	}*/	
			if (eventList.size() - preRegEventCount > eventsPanicThreshold) {
				LOG.error("More than {} related events found for event {} (from {} events for sentence): - possible infinite loop; adding no more events for file ", 
						eventsPanicThreshold, eventID, totalEventSet.size()); 
				break;
			}
        	//break the loop is there are no new events detected
        	if(previousEventCount == eventList.size())
        		break; 	
		}
        
		return new Integer[] { triggerStartingID, eventStartingID };
	}
	
	/**
	 * search for events that act as subevents in a main event
	 * @param currentEvent
	 * @param vertex
	 * @param category
	 * @param totalEventSet
	 * @return
	 */
	private List<Event> searchForSubevents(Event currentEvent, Vertex vertex, String category, Set<Event> totalEventSet) {
		List<Event> subevents = new ArrayList<Event>();
		for(Event event : totalEventSet) {
            if(event.getEventCategory().equals(category) && event.getEventTrigger().getTriggerNodes().contains(vertex) &&
            		!checkLoopEffectsBetweenTwoRegulationEvents(currentEvent, event) ) {
            	subevents.add(event);
            }
		}
		return subevents;
	}
	
	/**
	 * postprocess raw graph matching-based event extraction results via postprocessing rules
	 * in order to produce A2 files with valid format in the next step
	 * @param sentenceEventSet
	 * @return
	 */
	public Set<Event> postprocessRawExtractedEvents(Set<Event> sentenceEventSet) {
		List<Event> eventList = new ArrayList<Event>(sentenceEventSet); 
		//handle events with only cause argument
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i); 
	    	if(!event.hasTheme()) { 
	    		Set<Vertex> triggersCause = event.getEventTrigger().getTriggerNodes();
	    		for(int j=0; j<eventList.size(); j++) {
	    			if(i==j) continue;
	    			Event e = eventList.get(j);
	    			if(!e.hasCause() && e.getEventCategory().equals(event.getEventCategory()) && !e.getEventThemes().contains(event.getEventCause())) {
	    				Set<Vertex> triggersTheme = e.getEventTrigger().getTriggerNodes();
	    				if( (triggersTheme.size() == 1 && triggersCause.size() > 1 && 
	    						triggersCause.contains(new ArrayList<Vertex>(triggersTheme).get(0)) ) || 
	    				        (triggersCause.size() == 1 && triggersTheme.size() > 1 && 
	    						triggersTheme.contains(new ArrayList<Vertex>(triggersCause).get(0)) ) ||
	    				        triggersTheme.equals(triggersCause)) {
	    					Event newEvent = new Event(e.getOriginalEventRule());
	    					newEvent.update(e);
	    					newEvent.setEventCause(event.getEventCause());
	    					if(event.isCauseEvent()) {
	    					    newEvent.setCauseEvent(event.getCauseEvent());	
	        	    		    newEvent.setCauseEventCategory(event.getCauseEventCategory());
	    					}
	    					eventList.add(newEvent);
	    				}
	    			}
	    		}
	    		event.setStatus(true);
	    	}
	    } 
		//reverse Regulation event types to other two regulation types
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i);
	    	if(event.getStatus()) continue;
	    	if(event.getEventCategory().equals("Regulation")) {
	    	    Vertex trigger;
	    	    if(event.getEventTrigger().getCenterNode() != null)
					trigger = event.getEventTrigger().getCenterNode();
				else {
					trigger = searchCenterNodeForAnnotationGraphNodes(event.getEventTrigger().getTriggerNodes(), event.getSentenceGraph());
					event.getEventTrigger().setCenterNodes(trigger);
				}
	    	    //check neighbors
	    	    Collection<Vertex> neighbors = event.getSentenceGraph().getNeighbors(trigger);
	    	    for(Vertex n : neighbors) {
	    	    	if(n.getCompareForm().matches("^.*positive.*$")) {
	    	    		event.setEventCategory("Positive_regulation");	
	    	    	}
	    	    	else if(n.getCompareForm().matches("^.*negative.*$")) {
	    	    		event.setEventCategory("Negative_regulation");	
	    	    	}
	    	    }
	    	}
	    }
		//remove duplicate events
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i); 
	    	if(event.getStatus()) continue;
	    	boolean flag = false;
	    	for(int j=0; j<eventList.size(); j++) {
    			Event e = eventList.get(j);
    			if( i==j || e.getStatus()) continue;
    			if(!event.getOriginalEventRule().getRuleID().equals(e.getOriginalEventRule().getRuleID()) &&
    		    		event.getEventCategory().equals(e.getEventCategory()) &&
    		    		event.hasCause() && e.hasCause() && event.getEventCause().equals(e.getEventCause()) &&
    		    		event.hasTheme() && e.hasTheme() && event.getEventThemes().equals(e.getEventThemes()) &&
    		    		event.getEventTrigger().equals(e.getEventTrigger())) {
    		    		    flag = true; break;
    		    }	
	    	}
	    	if(flag) event.setStatus(true); 
		}	
		//remove events that involve approximately duplicate triggers 
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i);
	    	if(event.getStatus() || event.getEventTrigger().getTriggerNodes().size() == 1) continue;
	    	List<Vertex> sorted = new ArrayList<Vertex>(event.getEventTrigger().getTriggerNodes());
    		Collections.sort(sorted, new MyNewComparator());
    		Vertex vStart = sorted.get(0);
    		Vertex vEnd = sorted.get(sorted.size()-1);
	    	for(int j=0; j<eventList.size(); j++) {
	    		Event e = eventList.get(j);
	    		if(i==j || e.getStatus() || !event.getEventCategory().equals(e.getEventCategory()) ||
	    				!event.getEventThemes().equals(e.getEventThemes()) ||
	    				(event.hasCause() && !e.hasCause()) || (!event.hasCause() && e.hasCause()) ||
	    				(event.hasCause() && e.hasCause() && !event.getEventCause().equals(e.getEventCause())) ) 
	    			continue;
	    		if(e.getEventTrigger().getTriggerNodes().size() == 1) {
	    		    Vertex k = new ArrayList<Vertex>(e.getEventTrigger().getTriggerNodes()).get(0);
	    		    if(k.getOffset() >= vStart.getOffset() && k.getOffset() + k.getWord().length() <= vEnd.getOffset() + vEnd.getWord().length()) {
	        			//if the node order is correct, keep the one containing more specific info
	        			if(vEnd.getTokenPosition() - vStart.getTokenPosition() + 1 != event.getEventTrigger().getTriggerNodes().size())
	        				event.setStatus(true);  
	        			else
	        				e.setStatus(true); 
	    		    	break;
	    		    }	
	    		}
	    		else {
	    			List<Vertex> sort = new ArrayList<Vertex>(e.getEventTrigger().getTriggerNodes());
	        		Collections.sort(sort, new MyNewComparator());
	        		Vertex kStart = sort.get(0);
	        		Vertex kEnd = sort.get(sort.size()-1);  
	        		if(kStart.getOffset() >= vStart.getOffset() && kEnd.getOffset() + kEnd.getWord().length() <= vEnd.getOffset() + vEnd.getWord().length()) {
	        			if(vEnd.getTokenPosition() - vStart.getTokenPosition() + 1 != event.getEventTrigger().getTriggerNodes().size())
	        				event.setStatus(true);  
    			        else
    			        	e.setStatus(true); 
	    		    	break;
	    		    }	
	    		}
			}
		}	
		//remove regulation events that share triggers and themes of regulation events that contain Cause
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i);
	    	if(event.getStatus() || event.hasCause()) continue;
	    	for(int j=0; j<eventList.size(); j++) {
	    		Event e = eventList.get(j);
	    		if(i==j || e.getStatus() || !e.hasCause()) continue;
	    		if(event.getEventCategory().equals(e.getEventCategory()) && 
	    				event.getEventTrigger().equals(e.getEventTrigger()) && 
	    				event.getEventThemes().equals(e.getEventThemes())) {
	    			event.setStatus(true); 
    				break;
	    		}
			}
		}	
		//remove binding events that share triggers and themes of binding events that have more themes
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i);
	    	if(event.getStatus() || !event.getEventCategory().equals("Binding")) continue;
	    	for(int j=0; j<eventList.size(); j++) {
	    		Event e = eventList.get(j);
	    		if(i==j || e.getStatus() || !e.getEventCategory().equals("Binding")) continue;
	    		if(event.getEventTrigger().equals(e.getEventTrigger()) && 
	    				event.getEventThemes().size() < e.getEventThemes().size() ) {
	    			boolean flag = true;
	    			for(Vertex v : event.getEventThemes()) {
	    			    if(!e.getEventThemes().contains(v))	{
	    			    	flag = false; break;
	    			    }
	    			}
	    			if(flag) {
	    				event.setStatus(true); 
    				    break;
	    			}
	    		}
			}
		}
		//remove regulation events in which event theme is the same as event cause of other events with both theme and cause
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i);
	    	if(event.getStatus()) continue;
	    	if(!event.hasCause()) {
	    		for(int j=0; j<eventList.size(); j++) {
	    			Event e = eventList.get(j);
	    			if(e.getStatus()) continue;
	    			if(e.hasCause() && e.getEventCategory().equals(event.getEventCategory()) && 
	    					e.getEventTrigger().equals(event.getEventTrigger()) && 
	    					e.getEventCause().equals(new ArrayList<Vertex>(event.getEventThemes()).get(0))) {
	    				event.setStatus(true); 
	    				break;
	    			}
	    		}
	    	}
	    }
		/*
		//remove events in which subevents' trigger is the same as the main event trigger
		for(int i=0; i<eventList.size(); i++) {
	    	Event event = eventList.get(i);
	    	if(event.getStatus()) continue;
	    	if(event.isThemeEvent()) {
	    		Vertex theme = event.getThemeEvent();
	    		for(int j=0; j<eventList.size(); j++) {
	    			Event e = eventList.get(j);
	    			if(e.getStatus()) continue;
	    			Set<Vertex> triggers = e.getEventTrigger().getTriggerNodes();
	    			if(triggers.contains(theme) && e.getEventTrigger().equals(event.getEventTrigger()) ) {
	    				event.setStatus(true); 
	    				break;
	    			}
	    		}
	    	}
	    	if(event.isCauseEvent()) {
	    		Vertex cause = event.getCauseEvent();
	    		for(int j=0; j<eventList.size(); j++) {
	    			Event e = eventList.get(j);
	    			if(e.getStatus()) continue;
	    			Set<Vertex> triggers = e.getEventTrigger().getTriggerNodes();
	    			if(triggers.contains(cause) && e.getEventTrigger().equals(event.getEventTrigger()) ) {
	    				event.setStatus(true); 
	    				break;
	    			}
	    		}
	    	}
	    }*/
		//remove regulation events that involve subevents that are not existing
		while(true) { 
			int prevousRemovedEventCount = 0;
			for(Event event : eventList) 
				if(event.getStatus()) prevousRemovedEventCount++;
			
			for(int i=0; i<eventList.size(); i++) {
		    	Event event = eventList.get(i);
		    	if(event.getStatus()) continue;
		    	if(event.isThemeEvent()) {
		    		Vertex theme = event.getThemeEvent();
		    		boolean flag = false;
		    		for(int j=0; j<eventList.size(); j++) {
		    			Event e = eventList.get(j);
		    			if(i==j || e.getStatus()) continue;
		    			Set<Vertex> triggers = e.getEventTrigger().getTriggerNodes();
		    			if(triggers.contains(theme) && event.getThemeEventCategory().equals(e.getEventCategory())) {
		    				flag = true; break;
		    			}
		    		}
		    		if(!flag) {
		    			event.setStatus(true); 
		    			continue;
		    		}
		    	}
		    	if(event.isCauseEvent()) {
		    		Vertex cause = event.getCauseEvent();
		    		boolean flag = false;
		    		for(int j=0; j<eventList.size(); j++) {
		    			if(i==j) continue;
		    			Event e = eventList.get(j);
		    			if(e.getStatus()) continue;
		    			Set<Vertex> triggers = e.getEventTrigger().getTriggerNodes();
		    			if(triggers.contains(cause) && event.getCauseEventCategory().equals(e.getEventCategory())) {
		    				flag = true; break;
		    			}
		    		}
		    		if(!flag) {
		    			event.setStatus(true);  
		    			continue;
		    		}
		    	}
		    }
			int currentRemovedEventCount = 0;
			for(Event event : eventList) 
				if(event.getStatus()) currentRemovedEventCount++;
			//break the loop if there are no more events to remove
			if(currentRemovedEventCount == prevousRemovedEventCount) 
				break;
		}
		//generate a clean set that contain only events without removal sign
		Set<Event> postprocessedEventSet = new HashSet<Event>();
		for(Event event : eventList) {
		    if(!event.getStatus()) {
			    postprocessedEventSet.add(event); 
		    }    
		}
		return postprocessedEventSet;
	}
	
	/**
	 * check if two regulation events have loop effects that will get the program stuck
	 * for instance: trigger of one event is theme of the other while theme of one event is trigger of the other
	 * @param event
	 * @param e
	 * @return
	 */
	private static boolean checkLoopEffectsBetweenTwoRegulationEvents(Event event, Event e) {
		if( event.isThemeEvent() && event.getThemeEvent().equals(new ArrayList<Vertex>(e.getEventTrigger().getTriggerNodes()).get(0)) &&
				event.getThemeEventCategory().equals(e.getEventCategory()) && e.isThemeEvent() &&
				e.getThemeEvent().equals(new ArrayList<Vertex>(event.getEventTrigger().getTriggerNodes()).get(0)) &&
				e.getThemeEventCategory().equals(event.getEventCategory())) {
			return true;
		}
		else if( event.isCauseEvent() && event.getCauseEvent().equals(new ArrayList<Vertex>(e.getEventTrigger().getTriggerNodes()).get(0)) &&
				event.getCauseEventCategory().equals(e.getEventCategory()) && e.isCauseEvent() &&
				e.getCauseEvent().equals(new ArrayList<Vertex>(event.getEventTrigger().getTriggerNodes()).get(0)) &&
				e.getCauseEventCategory().equals(event.getEventCategory())) {
			return true;
		}
		else if( event.isThemeEvent() && event.getThemeEvent().equals(new ArrayList<Vertex>(e.getEventTrigger().getTriggerNodes()).get(0)) &&
				event.getThemeEventCategory().equals(e.getEventCategory()) && e.isCauseEvent() &&
				e.getCauseEvent().equals(new ArrayList<Vertex>(event.getEventTrigger().getTriggerNodes()).get(0)) &&
				e.getCauseEventCategory().equals(event.getEventCategory())) {
			return true;
		}
		else if( event.isCauseEvent() && event.getCauseEvent().equals(new ArrayList<Vertex>(e.getEventTrigger().getTriggerNodes()).get(0)) &&
				event.getCauseEventCategory().equals(e.getEventCategory()) && e.isThemeEvent() &&
				e.getThemeEvent().equals(new ArrayList<Vertex>(event.getEventTrigger().getTriggerNodes()).get(0)) &&
				e.getThemeEventCategory().equals(event.getEventCategory())) {
			return true;
		}
		else return false;
	}
	
	/**
	 * retrieve raw events directly from graph matching results of one event rule
	 * @param rule
	 * @param matchings
	 * @param sentenceGraph
	 * @param originalRule
	 * @return
	 */
	private Set<EventRuleMatch> getEventsFromMatchingsOfOneRule(EventRule rule, Map<Double, List< Map<Vertex, Vertex>>> matchings,
			DirectedGraph<Vertex, Edge> sentenceGraph, EventRule originalRule) {
		Map<Trigger, Map<Event, EventRuleMatch>> triggersToEvtDist = new HashMap<Trigger, Map<Event, EventRuleMatch>>();
		
		long startTime = System.currentTimeMillis();
		allmatchings:
		for(Double distance : matchings.keySet()) {
    		for(Map<Vertex, Vertex> m : matchings.get(distance)) {
    			Event event = new Event(originalRule);
    			Set<Vertex> triggers = new HashSet<Vertex>();
    			Set<Vertex> themes = new HashSet<Vertex>();
    			Vertex cause = null;
    			for (Map.Entry<Vertex, Vertex> entry : m.entrySet()) {
					if (System.currentTimeMillis() - startTime > 30000) {
						LOG.error("Giving up after 30 seconds extraction for a single rule: {}",
							rule);
						break allmatchings;
					}
    			    Vertex r = entry.getKey();
    			    Vertex s = entry.getValue();
    			    if(r.isTrigger())
    			    	triggers.add(s);
    			    if(rule.hasTheme() && rule.getEventThemes().contains(r))
    			    	themes.add(s);
    			    if(rule.hasCause() && rule.getEventCause().equals(r))
    			    	cause = s;
    			}
    			if(triggers.isEmpty()) {
    				System.out.println("New Rule " + rule);
    				System.out.println("Original Rule " + originalRule);
    				throw new RuntimeException("The event doesn't have a trigger, please check " + m);
    			}
    			Trigger trigger = new Trigger(triggers);
    			event.setEventCategory(rule.getEventCategory());
    			event.setEventTrigger(trigger);
    			event.setSentenceGraph(sentenceGraph);
    			if(rule.hasTheme() && !rule.hasCause()) {
	    			event.setEventThemes(themes);
    				if(rule.isThemeEvent()) {
    	    			event.setThemeEvent(new ArrayList<Vertex>(themes).get(0));
    	    			event.setThemeEventCategory(rule.getThemeEventCategory());
    				}
    			}
    			else if(!rule.hasTheme() && rule.hasCause()) {
	    			event.setEventCause(cause);
    				if(rule.isCauseEvent()) {
    	    			event.setCauseEvent(cause);	
    	    			event.setCauseEventCategory(rule.getCauseEventCategory());
    				}
    			}
    			else if(rule.hasTheme() && rule.hasCause()) {
	    			event.setEventThemes(themes);
	    			event.setEventCause(cause);
    				if(rule.isThemeEvent() && !rule.isCauseEvent()) {
        	    		event.setThemeEvent(new ArrayList<Vertex>(themes).get(0));
        	    		event.setThemeEventCategory(rule.getThemeEventCategory());
    			    }
    			    else if(!rule.isThemeEvent() && rule.isCauseEvent()) {
        	    		event.setCauseEvent(cause);	
        	    		event.setCauseEventCategory(rule.getCauseEventCategory());
    			    }
    			    //both theme and cause are subevents
    			    else if(rule.isThemeEvent() && rule.isCauseEvent()){
        	    		event.setThemeEvent(new ArrayList<Vertex>(themes).get(0));	
        	    		event.setThemeEventCategory(rule.getThemeEventCategory());
        	    		event.setCauseEvent(cause);	
        	    		event.setCauseEventCategory(rule.getCauseEventCategory());
    			    }
    				//both theme and cause are proteins
    			    else { }
    			}
    			else throw new RuntimeException("The event doesn't have either theme or cause " + rule);

    			Map<Event, EventRuleMatch> matchesForTrigger = triggersToEvtDist.get(trigger);
    			if (matchesForTrigger == null) {
    				matchesForTrigger = new HashMap<Event, EventRuleMatch>();
    				triggersToEvtDist.put(trigger, matchesForTrigger);
    			}
    			EventRuleMatch newMatch = new EventRuleMatch(event, rule.getRuleID(), distance);
    			EventRuleMatch existing = matchesForTrigger.get(event);
    			if (existing == null || newMatch.distance < existing.distance) 
    				matchesForTrigger.put(event, newMatch); // only replace if distance is less or no old one
        	}
    	}
		if (LOG.isTraceEnabled()) {
			for (Trigger trigger : triggersToEvtDist.keySet())
				LOG.trace("Trigger {} has {} matches: {}", trigger.getTriggerNodes(),
						triggersToEvtDist.get(trigger).values().size(),
						triggersToEvtDist.get(trigger).values());
		}
		Set<EventRuleMatch> events = new HashSet<EventRuleMatch>();
		for (Map<Event, EventRuleMatch> matchesForTrigger : triggersToEvtDist.values()) {
			if (System.currentTimeMillis() - startTime > 30000) {
				LOG.error("Giving up (in trigger evaluation) after 30 seconds extraction for a single rule: {}",
					rule);
				break;
			}
			List<EventRuleMatch> singleMatchesForTrigger = new ArrayList<EventRuleMatch>(matchesForTrigger.values());
			Trigger trigger = singleMatchesForTrigger.get(0).event.getEventTrigger(); // for debug logs
			LOG.trace("Processing trigger {}", trigger.getTriggerNodes());
			if (eventsPerTriggerRuleSoftMax == -1 // default: include all matches
					|| singleMatchesForTrigger.size() <= eventsPerTriggerRuleSoftMax) {
				LOG.trace("Including all {} rule matches for trigger {}", singleMatchesForTrigger.size(),
						trigger.getTriggerNodes());
				events.addAll(singleMatchesForTrigger);
				continue;
			}
			Collections.sort(singleMatchesForTrigger, new EventMatchDistanceComparator());
			int topIdx = 0;
			int actualTopIdx;
			// special case: include everything with distance 0.0 regardless of soft max
			while (singleMatchesForTrigger.get(topIdx).distance == 0.0)
				++topIdx;
			if (topIdx > eventsPerTriggerRuleSoftMax) {
				actualTopIdx = topIdx;
			} else {
				int prevTopIdx = topIdx;
				while (true) { // find the right cutoff index:
					double topDist = singleMatchesForTrigger.get(topIdx).distance;
					while (singleMatchesForTrigger.get(++topIdx).distance == topDist)
						; // find first with different distance to current
					if (topIdx > eventsPerTriggerRuleSoftMax) { // we've found the boundary
						// just need to pick the higher or lower one as better:
						if (topIdx - eventsPerTriggerRuleSoftMax < eventsPerTriggerRuleSoftMax - prevTopIdx) 
							actualTopIdx = topIdx; // the top boundary is closer
						else  // the low boundary is closer to the target
							actualTopIdx = prevTopIdx;
						break;
					}
					prevTopIdx = topIdx;
				}
			}
			LOG.trace("Selected {} (dist {}) as top index, of {} matches for {}/{}", actualTopIdx, 
					singleMatchesForTrigger.get(actualTopIdx).distance, singleMatchesForTrigger.size(),
					trigger.getTriggerNodes(), rule);
			// now add everything that's within the amount we've selected
			events.addAll(singleMatchesForTrigger.subList(0, actualTopIdx));
		}
		return events;
	}
	

	/**
	 * evaluate the predicted events using gold event annotation
	 * and print the evaluation results
	 */
	public String evaluateEventPrediction(String eventEvalPath, String goldPath) {
		if (eventPredictionPath == null)
			throw new RuntimeException("Event prediction must be run before evaluation");
        FileUtil.deleteDirectory(new File(eventEvalPath));
		EventExtractionEvaluator evaluator = new EventExtractionEvaluator(eventPredictionPath, eventEvalPath, goldPath);
		String result = evaluator.getAggregateEvaluation();
		System.out.print(result);
		return result;
	} 
	
	/**
	 * retrieve event rule to documents map
	 * @return
	 */
	public Map<String, Map<EventRule, Set<String>>> getRuleToDocumentsMap() {
		return ruleTypeToRuleToImpactedDocuments;
	}
	
	/**
	 * retrieve document to events map
	 * @return
	 */
	public Map<String, List<Set<Event>>> getDocumentToEventsMap() {
		return documentToEvents;
	}
	
	/**
	 * retrieve last protein ID map
	 * @return
	 */
	public Map<String, Integer> getLastProteinIDMap() {
		return lastProteinIDOfEachDocument;
	}
	
	
	public Map<String, List<EventRule>> getSimpleEventRules() {
		return categorizedSimpleRules;
	}
	
	public Map<String, List<EventRule>> getPTMEventRules() {
		return categorizedPTMRules;
	}
	
	public Map<String, List<EventRule>> getComplexEventRules() {
		return categorizedComplexRules;
	}

	
	public void clearMemory() {
		categorizedComplexRules.clear();
		categorizedPTMRules.clear();
		categorizedSimpleRules.clear();
		documents.clear();
		ruleTypeToRuleToImpactedDocuments.clear();
		documentToEvents.clear();
	}
}

class MyComparator implements Comparator<Vertex> {
    @Override
    /**
     * compare two objects according to their field
     */
    public int compare(Vertex o1, Vertex o2) {  
      if (o1.getTokenPosition() < o2.getTokenPosition()) {
         return 1;
      } else if (o1.getTokenPosition() > o2.getTokenPosition()) {
         return -1;
      }
      return 0;
    }
}


class EventRuleMatch {
	Event event;
	String ruleId;
	double distance;
	
	public EventRuleMatch(Event event, String ruleId, double distance) {
		this.event = event;
		this.ruleId = ruleId;
		this.distance = distance;
	}
	
	public String toString() {
		return String.format("%s <rule %s; dist %.3f>", event, ruleId, distance);
	}
}


class EventMatchDistanceComparator implements Comparator<EventRuleMatch> {
/** Note: this comparator imposes orderings that are inconsistent with equals */
	@Override
	public int compare(EventRuleMatch o1, EventRuleMatch o2) {
		return (int) Math.signum(o1.distance - o2.distance);
	}
}
