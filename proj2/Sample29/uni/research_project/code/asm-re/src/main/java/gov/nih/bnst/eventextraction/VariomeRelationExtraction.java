package gov.nih.bnst.eventextraction;

import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileReaderUtil;
import edu.ucdenver.ccp.common.file.FileUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst.patternlearning.RelationRule;
import gov.nih.bnst.patternlearning.RuleParsingException;
import gov.nih.bnst.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.combine.training.CombineInfo;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

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

/**
 * Extract binary relations from the Variome corpus using an
 * approximate sub-graph matching algorithm implemented in
 * the class ASM.
 */
public class VariomeRelationExtraction {

    ////////////////////////
    // Instance Variables //
    ////////////////////////

    private static final Logger LOG = LoggerFactory.getLogger(VariomeRelationExtraction.class);

	/** path to the rule directory */
	private final String rulePath;

	/** the set of rules of simple types excluding PTM event types*/
	private Map<String, List<RelationRule>> relationRules;

    /** the test documents */
	private Map< String, ? extends List<? extends AnnotatedSentence>> documents;

	/** total relation rule count */
	private int totalRelationRuleCount = 0;

	public static final Map<String, Integer> DEFAULT_THRESHOLDS =
        new HashMap<String, Integer>(10);

	/** the subgraph distance thresholds for each relation type */
	private final Map<String, Integer> thresholds =
        new HashMap<String, Integer>(10); //SUBGRAPH_DISTANCE_THRESHOLD;

	/** the weights of the subgraph distance : ws, wl, wd */
	private final static int[] weights = {10, 10, 10};

	/**
     * Relation types. Additional types should be added to
     * this array as required
     */
	String[] relationTypes = {
        //TODO
    };

	/**
     * Global structure to store relationType->relationRule->impactedDocument
     * relation for relation rule optimization (synchronized to allow access
     * concurently by multiple processing thread).
     */
	Map<String, Map<RelationRule, Set<String>>> ruleTypeToRuleToImpactedDocuments =
        Collections.synchronizedMap(
            new HashMap<String, Map<RelationRule, Set<String>>>()
        );

	/**
     * Global structure to store document->relations relation for relation
     * rule optimization
     */
	Map<String, List<Set<Relation>>> documentToRelations =
        Collections.synchronizedMap(
            new HashMap<String, List<Set<Relation>>>()
        );

    /**
     * Path for storing predicted ann files and raw relation predictions
     * By default this is initialized using the value stored in
     * com.unimelb.biomed.extractor.SharedTaskHelper.
     */
	private String relationPredictionPath;

    /** Threads to use during relation extraction */
	private int extractionThreads = 1;

    /** synchronized, so multiple threads can access counter */
	private final AtomicInteger docsExtracted = new AtomicInteger(0);

	private int relationsPanicThreshold = 2000;

	/**
     * The maximum time for relation extraction in seconds
     * (-1 for no timeout). This is enforced by a wrapper which
     * stops waiting for results after a certain time
     */
	private int extractionHardTimeout = -1;

	/**
     * Whether to timeout internally during relation extraction
     * if any class of relations takes more than 120 seconds
     * (unrelated to extractionHardTimeout)
     */
	private boolean enableSoftTimeout = true;

    /** Relation xtraction times for each processed document */
	private Map<String, Long> extractionTimes =
        Collections.synchronizedMap(new HashMap<String, Long>());

    /**
     * Documents where processing has been aborted.
     * This typically occurs if relation extraction times out.
     */
	private Set<String> blacklistedDocIds;

    /** Default thresholds for relation extraction */
	static {
		DEFAULT_THRESHOLDS.put("has", 3);
		DEFAULT_THRESHOLDS.put("relatedTo", 3);
        DEFAULT_THRESHOLDS.put("Default", 10);
	}

    ////////////////////////
    // Class Constructors //
    ////////////////////////

    public VariomeRelationExtraction(
        DocumentProducer docColl,
        String rulePath,
		Map<String, Integer> overrideThresholds,
        int extractionThreads,
		int relationsPerTriggerRuleSoftMax
    ) {
		this(docColl, rulePath);
		thresholds.putAll(overrideThresholds); //override defaults
		LOG.debug("Thresholds in use are: {}", thresholds);
		this.extractionThreads = extractionThreads;
	}

	public VariomeRelationExtraction(
        DocumentProducer docColl,
        String rulePath,
		Map<String, Integer> overrideThresholds,
        int extractionThreads
    ) {
		this(docColl, rulePath, overrideThresholds, extractionThreads, -1);
	}

	public VariomeRelationExtraction(
        DocumentProducer docColl,
        String rulePath
    ) {
		this.rulePath = rulePath;
		this.relationRules = readRuleDirectory();
		this.documents = docColl.getIdsToAnnotatedSentences();
		initThresholds();
    }

    /**
     * Set the threshold of the number of relations in a
     * sentence before we give up
     */
	public void setRelationsPanicThreshold(int newValue) {
		relationsPanicThreshold = newValue;
	}

	/**
     * Sets the amount of time allowed for relation extraction
     * before timing out
     */
	public void setExtractionTimeout(int timeout) {
		extractionHardTimeout = timeout;
	}

	public void disableSoftTimeout() {
		enableSoftTimeout = false;
	}

    /**
     * Set extraction thresholds to the default values stored
     * with the class.
     * <p>
     * This will be invoked if no thresholds are passed
     * to the constructor.
     *
     * @param void
     * @return void
     */
	protected void initThresholds() {
		thresholds.putAll(DEFAULT_THRESHOLDS);
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
     * Read relation rules from the directory where stored
     */
    private Map<String, List<RelationRule>> readRuleDirectory() {
    	File directory = new File(rulePath);
	    if ( !directory.isDirectory() ) {
	    	throw new RuntimeException( "The provided diretory: "
				+ rulePath + " is not a directory. Please check." );
	    }
	    Map<String, List<RelationRule>> relationRules =
            new HashMap<String, List<RelationRule>>();
	    File[] listOfFiles = directory.listFiles();
	    for (File inputFile : listOfFiles) {
	    	if (! inputFile.isFile() ||! inputFile.getName().matches("^\\S+\\.\\S+$")) {
                LOG.debug("Skipping rule file {}", inputFile);
                continue;
            }
			BufferedReader input;
	    	try {
				input = FileReaderUtil.initBufferedReader(inputFile, CharacterEncoding.UTF_8);
			} catch (FileNotFoundException e) {
				throw new RuntimeException("Unable to open the input file: "
						+ inputFile.getName(), e);
			}
			if( !inputFile.getName().split("\\.")[1].equals("rule") ) {
				//continue;
				throw new RuntimeException("The rule file name: "
						+ inputFile.getName() + " is not valid. Please check.");
			}

            //Add new categorized rule
			String category = inputFile.getName().split("\\.")[0];
            List<RelationRule> rules = readRuleFile(input, category);
            LOG.info("Read {} rules of type {} from file {}", rules.size(), category, inputFile.getName());
            if (relationRules.get(category) != null) {
                relationRules
                    .get(category)
                    .addAll(rules);
            }
            else {
                relationRules.put(category, rules);
            }
		    totalRelationRuleCount = rules.size();
	    }

	    return relationRules;
	}

    /**
	 * Choose the center node in order to keep only one graph node for each annotation
	 * the criteria is based on the Vertex connectivity
	 * @return
	 */
	private Vertex searchCenterNodeForAnnotationGraphNodes(
        Set<Vertex> graphNodes,
        DirectedGraph<Vertex, Edge> graph
    ) {
		//directly return the Vertex if the node set only has one node
		if(graphNodes.size() == 1)
		    return new ArrayList<Vertex>(graphNodes).get(0);
		//sort the graph nodes first from small position to big position
		List<Vertex> sorted = new ArrayList<Vertex>(graphNodes);
		Collections.sort(sorted, new MyRelationComparator());
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
	private static List<RelationRule> readRuleFile(
        BufferedReader input,
        String category
    ) {
		LOG.info("Reading rules for category {}", category);
		List<RelationRule> rules = new ArrayList<RelationRule>();
		String line = null;
		try {
			while ((line = input.readLine()) != null) {
				if (line.trim().length() == 0)
					continue;
				line = line.trim();
				LOG.info("Reading rule line '{}'", line);
				try {
					RelationRule rule = new RelationRule(line, category);
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
	 * main implementation of relation extraction
	 */
	public void relationExtractionByMatchingRulesWithSentences(
        final String relationPredictionPath,
        final String relationType
    ) {
		LOG.info("Running relation extraction for relation type {}; soft timeouts are {}", relationType, enableSoftTimeout ? "ENABLED" : "DISABLED");
		this.relationPredictionPath = relationPredictionPath;
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
					extractForSingleDocument(
                        relationPredictionPath,
                        fileName,
                        relationType
                    );
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

	protected void extractForSingleDocument(
        String relationPredictionPath,
        String fileName,
        String relationType
    ) {
		LOG.debug("Extracting relations for '{}'", fileName);
		long startTime = System.currentTimeMillis();
        int docIndex = docsExtracted.incrementAndGet();

		//Initialize output files
    	File outputFile = new File(relationPredictionPath, fileName + ".ann");
    	File rawOutputFile = new File(relationPredictionPath, fileName + ".raw");
    	outputFile.getParentFile().mkdirs();
    	BufferedWriter output;
    	BufferedWriter rawOutput;
    	try {
			output = FileWriterUtil.initBufferedWriter(
                outputFile,
                CharacterEncoding.UTF_8,
				WriteMode.OVERWRITE,
                FileSuffixEnforcement.OFF
            );
			rawOutput = FileWriterUtil.initBufferedWriter(
                rawOutputFile,
                CharacterEncoding.UTF_8,
                WriteMode.OVERWRITE,
                FileSuffixEnforcement.OFF
            );
		} catch (FileNotFoundException e) {
			LOG.error("Problem opening output file: {}", outputFile);
			throw new RuntimeException("Unable to open the output file: " + outputFile.getPath(), e);
		}
    	LOG.debug("Opened output file {}", outputFile);

        try {
            int relationStartingID = 1;
			List<String> documentRelationList = new ArrayList<String>();
			List<RelationRuleMatch> docRawRelationMatches = new ArrayList<RelationRuleMatch>();
			int sentenceCount = 0;

            LOG.debug(
                "{} has {} sentences",
                fileName,
                documents.get(fileName).size()
            );
			for (AnnotatedSentence sentence : documents.get(fileName)) {

                int countSimpleRelations = 0;
                Set<Relation> totalRelationSet = new HashSet<Relation>();
    			Set<Relation> relations = new HashSet<Relation>();

                long simplerulesStart = System.currentTimeMillis();

    			for(String category : relationRules.keySet()) {
                    if (!category.equals(relationType)) {
                        LOG.info("Category {} does not match target category {}, skipping", category, relationType);
                        continue;
                    }
                    LOG.info("Category {} matches target category {}, processing", category, relationType);
                    LOG.info("Relation rules for this category: {}", relationRules.get(category));
                    for (RelationRule rule: relationRules.get(category)) {
    					if (enableSoftTimeout && System.currentTimeMillis() - simplerulesStart > 120000) {
    						LOG.error(
                                "Event extraction (in simple rules) " +
                                "for {} took longer than 120 seconds; " +
                                "giving up", fileName
                            );
    						break;
    					}

                        //If there's no threshold passed in or set in the
                        //defaults, use a sensible default threshold
                        String thresholdsCategory;
                        if (!thresholds.containsKey(rule.getRelationCategory())) {
                            thresholdsCategory = "Default";
                        }
                        else {
                            thresholdsCategory = rule.getRelationCategory();
                        }

                        //Identify the sub-graph matches between the rule
                        //and the sentence.
                        ASM asm = new ASM(
                            rule,
                            sentence,
                            thresholds.get(thresholdsCategory),
                            weights
                        );
                        long preAsmTime = System.currentTimeMillis();
                        Map<Double, List< Map<Vertex, Vertex>>> matchings =
                            asm.getApproximateSubgraphMatchingMatches();
                        long asmTime = System.currentTimeMillis() - preAsmTime;
                        LOG.debug(
                            "Summary of matches for rule {}"
                            + " in sentence {}"
                            + " of document {}:",
                            rule.getRelationCategory(),
                            sentence.getSentenceID(),
                            fileName
                        );

                        if (asmTime > 60000 || LOG.isTraceEnabled())
        					LOG.warn(
                                "Took {} ms to find matches using ASM "
                                + "for {}: #{} with rule {}", asmTime,
        						fileName, sentence.getSentenceID(), rule
                            );

                        //Continue processing other rules if no matches found
                        if (matchings.size() == 0)
                            continue;
                        LOG.debug(
                            "For rule {}:{}, found {} matches",
                            rule.getRelationCategory(),
                            rule.getRuleID(),
                            matchings.size()
                        );
        				LOG.debug("  (complete rule: {})", rule);

                        //Extract a set of RuleMatch objects from the subgraph
                        //matches.
    					Set<RelationRuleMatch> matches =
                            getRelationsFromMatchingsOfOneRule(
                                rule,
                                matchings,
    							sentence.getDependencyGraph().getGraph(),
                                rule
                            );

                        //Store the rule matches
    					docRawRelationMatches.addAll(matches);

                        //Extract a set of Relation objects from the RuleMatch
                        //objects and store them in the set of Relations for this
                        //this sentence
                        for(RelationRuleMatch rrm : matches) {
    						Relation relation = rrm.relation;
    						LOG.debug("Storing relation {}", relation);
    						countSimpleRelations++;
    						relations.add(relation);
    					}
                        LOG.debug(
                            "From simple rule {} with {} matches, got {} relations",
                            rule, matchings.size(), relations.size()
                        );
                    }
			    } //End of rule processing loop

                //Populate the two global structures for rule optimization use
                totalRelationSet.addAll(relations);
                LOG.debug(
                    "Document {} now has {} relations",
                    fileName,
                    totalRelationSet.size()
                );

                //Populate the map from rule type -> rule object -> document
                for(Relation rel : totalRelationSet) {
                    String originalRelationCategory =
                        rel.getOriginalRelationRule().getRelationCategory();

                    //Map already has the category
                    if (
                        ruleTypeToRuleToImpactedDocuments
                            .containsKey(originalRelationCategory)
                    ) {
                        //Map already has the rule, add the document
    			        if (
                            ruleTypeToRuleToImpactedDocuments
                                .get(originalRelationCategory)
                                .containsKey(rel.getOriginalRelationRule())
                        ) {
    			        	ruleTypeToRuleToImpactedDocuments
                                .get(originalRelationCategory)
                                .get(rel.getOriginalRelationRule())
                                .add(fileName);
    			        }
                        //Map doesn't have the rule, create a new set
                        //of documents
    			        else {
    			        	Set<String> impactedDocuments =
                                new HashSet<String>();
        			    	impactedDocuments.add(fileName);
    			        	ruleTypeToRuleToImpactedDocuments
                                .get(originalRelationCategory)
                                .put(
                                    rel.getOriginalRelationRule(),
                                    impactedDocuments
                                );
    			        }
    			    }
                    //Map does not have the category
                    //Create a new map from rule object -> document
    			    else {
    			    	Map<RelationRule, Set<String>> ruleToImpactedDocuments =
                            new HashMap<RelationRule, Set<String>>();
    			    	Set<String> impactedDocuments = new HashSet<String>();
    			    	impactedDocuments.add(fileName);
    			    	ruleToImpactedDocuments.put(
                            rel.getOriginalRelationRule(),
                            impactedDocuments
                        );
    			    	ruleTypeToRuleToImpactedDocuments.put(
                            rel.getOriginalRelationRule().getRelationCategory(),
                            ruleToImpactedDocuments
                        );
    			    }
    			}

                //Build map from document name to set of relations,
                //one set per sentence
                if(documentToRelations.containsKey(fileName)) {
    				documentToRelations
                        .get(fileName)
                        .add(totalRelationSet);
                }
                else {
    				List<Set<Relation>> list = new ArrayList<Set<Relation>>();
    				list.add(totalRelationSet);
    				documentToRelations.put(fileName, list);
    			}

    			//Postprocess raw relations
			    if(!totalRelationSet.isEmpty())
			    	totalRelationSet = postprocessRawExtractedRelations(
                        totalRelationSet
                    );

                //Convert postprocessed raw relations to ANN format
                //Recall documentRelationList is a list of strings
                //This is modified in place by this method to accumulate
                //a list of ANN formatted rules
                LOG.debug(
                    "({} relations after post-processing)",
                    totalRelationSet.size()
                );
			    if(!totalRelationSet.isEmpty()) {
			    	Integer[] currentIDs = rawRelationsToANNStrings(
                        totalRelationSet,
                        relationStartingID,
			    		documentRelationList
                    );
                    relationStartingID = currentIDs[0];
			    }

                LOG.debug(
                    "Finished processing sentence #{}",
                    sentence.getSentenceID()
                );

            } // End of sentence processing loop

            //Log the findings for this document
			LOG.debug(
                "Found {} relations for document",
				documentRelationList.size()
            );
		    for(String relation : documentRelationList) {
		    	output.write(relation + "\n");
		    }
            for (RelationRuleMatch rrm : docRawRelationMatches) {
				rawOutput.write(rrm + "\n");
            }

            rawOutput.close();
			output.close();

            long endTime = System.currentTimeMillis();
			extractionTimes.put(fileName, endTime - startTime);
			LOG.debug(
                "Extracting {} relations from '{}' ({} of {}) took {} ms",
				documentRelationList.size(),
                fileName,
				docIndex,
                documents.size(),
                endTime - startTime
            );
		} catch (IOException e) {
			throw new RuntimeException(
                "Unable to process the output file: ", e
            );
		}
	}

	/**
	 * convert raw graph matching relation extraction results
     * into shared task ann format
     *
     * @param totalRelationSet
	 * @param relationID
	 * @param relationList
	 * @return
	 */
	public Integer[] rawRelationsToANNStrings(
        Set<Relation> totalRelationSet,
        int relationID,
        List<String> relationList
    ) {
		int currentRelationID = relationID;
		Set<String> detectedRelations = new HashSet<String>();

		for(Relation relation : totalRelationSet) {
            //Add relation identifier
            StringBuilder sb = new StringBuilder();
			sb.append("R" + currentRelationID + "\t");
    		relation.setRelationID(currentRelationID);
	    	sb.append(relation.getRelationCategory());
            //Add relation arguments (themes)
            if(relation.getRelationThemes().size() > 1) {
		    	List<Vertex> sorted = new ArrayList<Vertex>(
                    relation.getRelationThemes()
                );
                LOG.info("Creating relation string with themes: {}", sorted);
	    		Collections.sort(sorted, new MyNewComparator());
	    		sb.append(" Arg1:" + sorted.get(0).getArgumentID());
				for(int i=1; i<sorted.size(); i++) {
					sb.append(" Arg" + (i+1) + ":" + sorted.get(i).getArgumentID());
				}
		    }
            LOG.info("Final relation string: {}", sb.toString());
            relationList.add(sb.toString());
            currentRelationID += 1;
		}

		return new Integer[] { currentRelationID };
	}

	/**
	 * Postprocess raw graph matching-based relation extraction results
     * via postprocessing rules in order to produce ann files with valid
     * format in the next step
     *
     * @param raw set of relations
	 * @return post-processed set of relations
	 */
	public Set<Relation> postprocessRawExtractedRelations(
        Set<Relation> sentenceRelationSet
    ) {

        List<Relation> relationList =
            new ArrayList<Relation>(sentenceRelationSet);

		//Remove duplicate relations
		for(int i = 0; i < relationList.size(); i++) {
	    	Relation relation = relationList.get(i);
	    	if(relation.getStatus())
                continue;
	    	boolean flag = false;
	    	for(int j = 0; j < relationList.size(); j++) {
    			Relation r = relationList.get(j);
    			if( i==j || r.getStatus())
                    continue;
    			if(
                    !relation.getOriginalRelationRule().getRuleID().equals(r.getOriginalRelationRule().getRuleID())
                    && relation.getRelationCategory().equals(r.getRelationCategory())
                    && relation.hasTheme()
                    && r.hasTheme()
                    && relation.getRelationThemes().equals(r.getRelationThemes())
                ) {
    		        flag = true;
                    break;
    		    }
	    	}
	    	if(flag)
                relation.setStatus(true);
		}

		//generate a clean set that contain only relations without removal sign
		Set<Relation> postprocessedRelationSet = new HashSet<Relation>();
		for(Relation relation : relationList) {
		    if(!relation.getStatus()) {
			    postprocessedRelationSet.add(relation);
		    }
		}

        return postprocessedRelationSet;
	}

	/**
	 * Retrieve set of RelationRuleMatch objects directly from
     * graph matching results between a single relation rule
     * and a sentence graph.
	 *
     * @param rule
	 * @param matchings
	 * @param sentenceGraph
	 * @param originalRule
	 * @return
	 */
	private Set<RelationRuleMatch> getRelationsFromMatchingsOfOneRule(
        RelationRule rule,
        Map<Double, List< Map<Vertex, Vertex>>> matchings,
		DirectedGraph<Vertex, Edge> sentenceGraph,
        RelationRule originalRule
    ) {
        //Map from relation categories -> relation objects -> match objects
		Map<String, Map<Relation, RelationRuleMatch>> relationCategoriesToEvtDist =
            new HashMap<String, Map<Relation, RelationRuleMatch>>();

		long startTime = System.currentTimeMillis();

        //Loop over matching graphs within each match
        //Note that a "match" is signified by a numeric value (Double)
        //indicating the quality of the match
        allmatchings:
        for(Double distance : matchings.keySet()) {
    		for(Map<Vertex, Vertex> match : matchings.get(distance)) {

                //Initialize new relation using matching rule
                Relation relation = new Relation(originalRule);

                //Reset themes of new relation using themes in match
                Set<Vertex> themes = new HashSet<Vertex>();

                //Determines which vertices from the rule exist within
                //the matching sentence, then uses those vertices to
                //set the themes of the new relation.
                for (Map.Entry<Vertex, Vertex> entry : match.entrySet()) {
					if (System.currentTimeMillis() - startTime > 30000) {
						LOG.error("Giving up after 30 seconds extraction for a single rule: {}",
							rule);
						break allmatchings;
					}
    			    Vertex ruleVertex = entry.getKey();
    			    Vertex sentenceVertex = entry.getValue();

                    //If the themes of the rule contain the vertex in the match,
                    //add the sentence vertex to the themes of this relation.
                    if (rule.hasTheme() && rule.getRelationThemes().contains(ruleVertex))
    			    	themes.add(sentenceVertex);
    			}

                relation.setRelationThemes(themes);

                //Reset sentence graph and category of new relation using rule
                relation.setRelationCategory(rule.getRelationCategory());
                relation.setSentenceGraph(sentenceGraph);

                //Build up a mapping from relations to their rule match
    			Map<Relation, RelationRuleMatch> matchesForCategory =
                    relationCategoriesToEvtDist.get(rule.getRelationCategory());

                //If we don't have this category in the mapping yet
                if (matchesForCategory == null) {
    				matchesForCategory = new HashMap<Relation, RelationRuleMatch>();
    				relationCategoriesToEvtDist.put(
                        rule.getRelationCategory(),
                        matchesForCategory
                    );
    			}

                //Add mapping from relation -> match to this category
                //Note we only replace if distance is less (better than)
                //the existing match, or if there is no exiting match.
    			RelationRuleMatch newMatch =
                    new RelationRuleMatch(
                        relation,
                        rule.getRuleID(),
                        distance
                    );
    			RelationRuleMatch existing =
                    matchesForCategory.get(relation);
    			if (existing == null || newMatch.distance < existing.distance)
                    matchesForCategory.put(relation, newMatch);
        	}
    	} //End of graph matching loop

        //Log our results
		if (LOG.isTraceEnabled()) {
			for (String category : relationCategoriesToEvtDist.keySet()) {
				LOG.trace(
                    "Relation category {} has {} matches: {}",
                    category,
					relationCategoriesToEvtDist.get(category).values().size(),
					relationCategoriesToEvtDist.get(category).values()
                );
            }
		}

        //Gets the set of relationship matches to return
		Set<RelationRuleMatch> relations = new HashSet<RelationRuleMatch>();
		for (Map<Relation, RelationRuleMatch> matchesForCategory : relationCategoriesToEvtDist.values()) {
			if (System.currentTimeMillis() - startTime > 30000) {
				LOG.error(
                    "Giving up (in trigger evaluation) after "
                    + "30 seconds extraction for a single rule: {}",
					rule
                );
				break;
			}
			List<RelationRuleMatch> singleMatchesForCategory =
                new ArrayList<RelationRuleMatch>(matchesForCategory.values());
			String category =
                singleMatchesForCategory.get(0).relation.getRelationCategory(); // for debug logs
			LOG.debug("Processing category {}", category);
			LOG.debug(
                "Including all {} rule matches for category {}",
                singleMatchesForCategory.size(),
				category
            );
			relations.addAll(singleMatchesForCategory);
        }

		return relations;
	}


	/**
	 * Evaluate the predicted relations using gold relation annotation
	 * and print the evaluation results
	 */
	public String evaluateRelationPrediction(
        String relationEvalPath,
        String goldPath,
        String rulesPath
    ) {
		if (relationPredictionPath == null)
			throw new RuntimeException(
                "Relation prediction must be run before evaluation"
            );
        FileUtil.deleteDirectory(new File(relationEvalPath));
		VariomeRelationExtractionEvaluator evaluator =
            new VariomeRelationExtractionEvaluator(
                relationPredictionPath,
                relationEvalPath,
                goldPath,
                rulesPath
            );
		String result = evaluator.getAggregateEvaluation();
		System.out.print(result);
		return result;
	}

	/**
	 * retrieve relation rule to documents map
	 * @return
	 */
	public Map<String, Map<RelationRule, Set<String>>> getRuleToDocumentsMap() {
		return ruleTypeToRuleToImpactedDocuments;
	}

	/**
	 * retrieve document to events map
	 * @return
	 */
	public Map<String, List<Set<Relation>>> getDocumentToRelationsMap() {
		return documentToRelations;
	}

	public Map<String, List<RelationRule>> getRelationRules() {
		return relationRules;
	}

	public void clearMemory() {
		relationRules.clear();
		documents.clear();
		ruleTypeToRuleToImpactedDocuments.clear();
		documentToRelations.clear();
	}
}

class MyRelationComparator implements Comparator<Vertex> {
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


class RelationRuleMatch {
	Relation relation;
	String ruleId;
	double distance;

	public RelationRuleMatch(Relation relation, String ruleId, double distance) {
		this.relation = relation;
		this.ruleId = ruleId;
		this.distance = distance;
	}

	public String toString() {
		return String.format("%s <rule %s; dist %.3f>", relation, ruleId, distance);
	}
}


class RelationMatchDistanceComparator implements Comparator<RelationRuleMatch> {
/** Note: this comparator imposes orderings that are inconsistent with equals */
	@Override
	public int compare(RelationRuleMatch o1, RelationRuleMatch o2) {
		return (int) Math.signum(o1.distance - o2.distance);
	}
}
