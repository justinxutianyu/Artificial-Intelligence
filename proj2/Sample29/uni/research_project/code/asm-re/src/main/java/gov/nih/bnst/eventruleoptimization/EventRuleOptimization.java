package gov.nih.bnst.eventruleoptimization;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.hash.HashCode;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hasher;
import com.google.common.hash.Hashing;
import com.unimelb.biomed.extractor.SharedTaskHelper;
import com.tantaman.commons.concurrent.Parallelizer;

import gov.nih.bnst.patternlearning.EventRule;
import gov.nih.bnst.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst.preprocessing.annotation.Trigger;
import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileReaderUtil;
import edu.ucdenver.ccp.common.file.FileUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import gov.nih.bnst.eventextraction.Event;
import gov.nih.bnst.eventextraction.EventExtraction;
import gov.nih.bnst.eventextraction.EventExtractionEvaluator;

public class EventRuleOptimization {

	private static final Logger LOG = LoggerFactory.getLogger(EventRuleOptimization.class);

	/** event extraction class object */
	EventExtraction eventExtractor;

	/** store the last protein ID in each document for indexing triggers in later process */
	Map<String, Integer> lastProteinIDOfEachDocument;

	/** path to the predicted event evaluation directory */
	private static final String PATH_TO_EVENT_EVALUATION = SharedTaskHelper.TUNING_EVAL_DIR;

	/** path to the predicted event directory for optimization */
	private static final String PATH_TO_PREDICTED_EVENT_FOR_OPTIMIZATION = SharedTaskHelper.TUNING_PREDICTIONS_DIR;

	/** path to write the optimized event rules */
	private final String optimRulesDir;

	/** rule optimization accuracy threshold */
	private double ruleAccuracyThreshold = 0.25;

	/** simple event types */
	String[] simpleEventTypes = {
        "Gene_expression",
        "Transcription",
        "Binding",
        "Localization",
        "Protein_catabolism"
    };

	/** PTM event types */
	String[] ptmEventTypes = {
        "Acetylation",
        "Deacetylation",
        "Phosphorylation",
        "Protein_modification",
        "Ubiquitination"
    };

	/**
     * The document producer for the tuning (optimization)
     * documents - which could be the same as the dev set
     */
	private DocumentProducer docProd;

	/** The thresholds for the event extraction */
	private Map<String, Integer> extractionThresholds;

	/** The path to the gold .a1/.a2 annotations for the tuning files */
	private final String tuningGoldDir;

	/** the number of threads to use in event extraction */
	private int nProcThreads = 1;

	/**
     * The threshold at which we stop extracting events
     * because we're wildly overgenerating
     */
	private int eventsPanicThreshold = 2000;

	/** (DEPRECATED) passed through to event extraction; only get around this
	 * many rule matches per trigger, to try and stop over-generation
	 *
	 * -1 (the default) is unbounded; any subgraph matches (within the subgraph match tolerance)
	 * will be used
	 */
	private int eventsPerTriggerRuleSoftMax = -1;

	private final String rawRulesDir;

	private final AtomicInteger numberofLowerPerformingRules = new AtomicInteger();

	/** don't allow event extraction for a single document to take longer than this */
	private int extractionTimeout = -1;

	private Set<String> excludedDocIds;

	public enum ContribEvalMode {
		FULL,
		FILTERED,
		BOTH
	}

	private ContribEvalMode evalMode = ContribEvalMode.FILTERED;

	private boolean enableSoftTimeouts = true;


	/**
	 * Constructor to start the initial evaluation based on the original rule set
	 * @param docProd - the source of the documents to optimize over
	 * @param rawRulesDir - the original unmodified rule directory
	 * @param optimRulesDir - the directory where the newly optimized rules should be written
	 * @param tuningGoldDir - the directory with the gold data for the tuning documents in `docProd`
	 * @throws IOException - if the optimized rules directory cannot be created
	 */
	public EventRuleOptimization (
        DocumentProducer docProd,
        String rawRulesDir,
		String optimRulesDir,
        String tuningGoldDir,
        Map<String, Integer> extractionThresholds,
		int nProcThreads
    ) {
		this.docProd = docProd;
		this.tuningGoldDir = tuningGoldDir;
		this.optimRulesDir = optimRulesDir;
		this.rawRulesDir  = rawRulesDir;
		this.nProcThreads = nProcThreads;
		this.extractionThresholds = extractionThresholds;
    }

	/**
     * Specify a new threshold (instead of the default 2000) at which to
	 * give up event extraction
	 * @param thresh
	 */
	public void setEventsPanicThreshold(int thresh) {
		eventsPanicThreshold = thresh;
	}

	public void setExtractionTimeout(int timeout) {
		extractionTimeout  = timeout;
	}

	/** specify a new target accuracy threshold which we optimize towards,
	 * instead of the default 0.25 */
	public void setRuleAccuracyThreshold(double newThresh) {
		ruleAccuracyThreshold = newThresh;
	}

    /**
     * Initial pass for rule optimization, setting up
     * the necessary pre-conditions for calling the
     * iterativeRuleOptimizationProcess method.
     */
	protected void startOptimization() {
        //Create directory for optimized rules
        //Delete any existing rules, and create
        //starting rule set using raw rules.
        try {
			File optimRulesFile = new File(optimRulesDir);
			FileUtil.deleteDirectory(optimRulesFile);
			FileUtil.copyDirectory(new File(rawRulesDir), optimRulesFile);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

        //Set up the event extractor for the first run
        eventExtractor = new EventExtraction(
            this.docProd,
            this.optimRulesDir,
            this.extractionThresholds,
            this.nProcThreads,
			this.eventsPerTriggerRuleSoftMax
        );
		if (!enableSoftTimeouts)
			eventExtractor.disableSoftTimeout();
		eventExtractor.setEventsPanicThreshold(this.eventsPanicThreshold);
		eventExtractor.setExtractionTimeout(extractionTimeout);

        //Extract and evaluate a set of events
        eventExtractor.eventExtractionByMatchingRulesWithSentences(
            PATH_TO_PREDICTED_EVENT_FOR_OPTIMIZATION
        );
		eventExtractor.evaluateEventPrediction(
            PATH_TO_EVENT_EVALUATION,
            this.tuningGoldDir
        );

        //Store docs with long extraction times and leave them until later
		excludedDocIds = eventExtractor.docIdsWithLongExtractionTimes(15000);
		LOG.info(
            "Temporarily removing {} documents with " +
            "extraction times of 15 seconds or more: {}",
			excludedDocIds.size(),
            excludedDocIds
        );
		lastProteinIDOfEachDocument = docProd.getLastProteinIDOfDocuments();
	}

	public void optimize() {
		LOG.info(
            "In optimization, soft timeouts are {}",
            enableSoftTimeouts ? "ENABLED" : "DISABLED"
        );
		startOptimization();
        //TODO: Figure out why iterative optimization
        //      is killing all our rules
        iterativeRuleOptimizationProcess();
	}

	public EventRuleOptimization(DocumentProducer docProd, String rawRulesDir,
			String optimRulesDir, String tuningGoldDir) {
		this(
            docProd,
            rawRulesDir,
            optimRulesDir,
            tuningGoldDir,
            new HashMap<String, Integer>(0),
            1
        );
	}

	public int evaluateContributionOfEachRule() {
        //Ranking(optimization) results for each rule
		numberofLowerPerformingRules.set(0);

        //Structure to store
        //eventType->eventRule->impactedDocument
        //relationship for event rule optimization
		Map<String, Map<EventRule, Set<String>>> ruleTypeToRuleToImpactedDocuments =
            eventExtractor.getRuleToDocumentsMap();

        if (ruleTypeToRuleToImpactedDocuments.size() == 0)
			LOG.error("No rules to document mapping found");

        //Structure to store document->events relationship for event rule
        //optimization
		final Map<String, List<Set<Event>>> documentToEvents =
            eventExtractor.getDocumentToEventsMap();

        //Assess the quality of each rule when applied to the documents
        //it has been matched to
		for (String category : ruleTypeToRuleToImpactedDocuments.keySet()) {
            //Mapping from rule -> docs, indicating which rules have
            //been matched to what docs.
            final Map<EventRule, Set<String>> categoryImpactedDocs =
                ruleTypeToRuleToImpactedDocuments.get(category);

            //The set of rules from the mapping above
            Set<EventRule> rules = categoryImpactedDocs.keySet();

            //Main rule evaluation loop: evaluates each of the rules
            //from the set of above against the documents in which
            //it has been detected.
            for (EventRule rule : rules) {
				evaluateSingleRule(
                    rule,
                    categoryImpactedDocs,
                    documentToEvents
                );
            }
        }
	    return numberofLowerPerformingRules.get();
	}

	protected void evaluateSingleRule (
        EventRule rule,
        Map<EventRule, Set<String>> categoryImpactedDocs,
		Map<String, List<Set<Event>>> documentToEvents
    ) {
		long startTime = System.currentTimeMillis();
		int currentAnswer = 0;
        int currentMatch = 0;
		String uniqueSubDir = rule.getEventCategory() + "-" + rule.getRuleID();

         //Init optimization and evaluation directories
         //Note each directory is unique, to avoid clashes
         //between threads.
		File optimDir = new File(
            PATH_TO_PREDICTED_EVENT_FOR_OPTIMIZATION,
			uniqueSubDir
        );
		File evalDir = new File(
            PATH_TO_EVENT_EVALUATION,
            uniqueSubDir
        );
		optimDir.mkdirs();
		evalDir.mkdirs();

        LOG.debug(
            "Evaluating rule {} in directory {}",
            rule,
            uniqueSubDir
        );
		LOG.debug(
            "Impacted documents are: {}",
            categoryImpactedDocs.get(rule)
        );

        //Loop over each document where a rule match has been found
        //This mimics the extraction of events for a single document
        //in the EventExtraction class.
        for(String pmid : categoryImpactedDocs.get(rule)) {
			LOG.trace(
                "Checking impacted document {} for rule {}",
                pmid,
                rule.getRuleID()
            );

			//Create a file for the prediction?
            //TODO: verify
			File outputFile = new File(optimDir, pmid + ".a2");
			outputFile
                .getParentFile()
                .mkdirs();

            //Initial conditions for event prediction
            int triggerStartingID = lastProteinIDOfEachDocument.get(pmid);
			int eventStartingID = 0;
			List<String> documentTriggerList = new ArrayList<String>();
			List<String> documentEventList = new ArrayList<String>();

            //Loop over each set of events detected in this document
            for(Set<Event> set : documentToEvents.get(pmid)) {
				Set<Event> updatedEventSet = new HashSet<Event>();

                //Loop over events in set
                //TODO: Don't quite understand purpose of this loop
                //      We're obviously screening events somehow,
                //      because the next step has a check to ensure the
                //      updated event set isn't empty.
                for(Event event : set) {
					if(!event.getOriginalEventRule().equals(rule)) {
						Event newEvent =
                            new Event(event.getOriginalEventRule());
						newEvent.update(event);
						updatedEventSet.add(newEvent);
					}
				}

                //If our updated set of events isn't empty, post-process
                //events and generate A2 strings.
				if(!updatedEventSet.isEmpty()) {
			    	//Postprocess raw events
					updatedEventSet =
                        eventExtractor.postprocessRawExtractedEvents(
                            updatedEventSet
                        );

                    //Convert postprocessed raw events to A2 format
					Integer[] currentIDs = eventExtractor.rawEventsToA2Strings(
                        updatedEventSet,
                        triggerStartingID,
                        eventStartingID,
			    		documentTriggerList,
                        documentEventList
                    );
					triggerStartingID = currentIDs[0];
			    	eventStartingID = currentIDs[1];
			    }
			}

            //Write predictions to output file
			BufferedWriter output;
			try {
				output = FileWriterUtil.initBufferedWriter(
                    outputFile,
                    CharacterEncoding.UTF_8,
					WriteMode.OVERWRITE,
                    FileSuffixEnforcement.OFF
                );

                for (String trigger : documentTriggerList)
					output.write(trigger + "\n");
				for (String event : documentEventList)
					output.write(event + "\n");

                output.close();
			} catch (FileNotFoundException e) {
				throw new RuntimeException(
                    "Unable to open the output file: "
					+ outputFile.getAbsolutePath(), e
                );
			} catch (IOException e) {
				throw new RuntimeException(
                    "Unable to process the output file: ", e
                );
			}
		}

        //Get a list of prediciton files we created above
        File[] listOfFiles = optimDir.listFiles();
		LOG.debug(
            "Evaluating {} files in {}",
            listOfFiles.length,
            optimDir
        );
		long preEvalTime = System.currentTimeMillis();

		int contributionAnswer = 0;
        int contributionMatch = 0;

		for (File inputFile : listOfFiles) {
            //Skip any invalid files
            if (!inputFile.isFile() || !inputFile.getName().matches("^\\S+\\.a2$"))
				continue;

            //Determine the contribution of this file
            //TODO: verify this.
			EventAnswerInfo contribInfo = determineContribution(
				new File(
                    PATH_TO_PREDICTED_EVENT_FOR_OPTIMIZATION,
                    inputFile.getName()
                ),
				inputFile
            );

            contributionAnswer += contribInfo.answer;
			contributionMatch += contribInfo.match;
		}

        LOG.debug(
            "There are {} answers and {} matches for rule {}",
            currentAnswer,
            currentMatch,
            rule.getRuleID()
        );
		long newEvalTime = System.currentTimeMillis() - preEvalTime;
		//remove the prediction_optimization folder for cleaning
		FileUtil.deleteDirectory(optimDir);

		LOG.trace(
            "Overall rule {} contributed {} matches from {} answers",
			rule,
            contributionMatch,
            contributionAnswer
        );

        //Removes low performing rules
        //TODO: Understand this logic
        if ((contributionAnswer > 0 && contributionMatch*1.0/contributionAnswer < ruleAccuracyThreshold)) {
			System.out.println(
                rule
                + "\t"
                + contributionAnswer
                + "\t"
                + contributionMatch
            );

            rule.setRemovalSign(true);

            LOG.trace(
                "Rule {} will be removed; " +
                "there are now {} poorly performing rules",
		    	rule.getRuleID(),
                numberofLowerPerformingRules.get()
            );

            numberofLowerPerformingRules.incrementAndGet();
		} else {
		    rule.setRemovalSign(false);
			LOG.trace(
                "Rule {} (contributed: {} matches from {} answers) " +
                " performs well enough to keep",
				rule,
                contributionMatch,
                contributionAnswer
            );
		}
		LOG.debug(
            "It took {} ms ({} in eval) to evaluate " +
            "rule '{}', affecting {} docs",
			System.currentTimeMillis() - startTime,
            newEvalTime,
            rule,
            categoryImpactedDocs.get(rule).size()
        );
	}


	private EventAnswerInfo determineContribution(File origFile, File newFile) {
		EventAnswerInfo contrib = null;
        EventAnswerInfo filtContrib = null;

         // use the full .a2 file
        if (evalMode == ContribEvalMode.FULL || evalMode == ContribEvalMode.BOTH) {
			contrib = determineContribFull(origFile, newFile);
        }

        if (evalMode == ContribEvalMode.FILTERED || evalMode == ContribEvalMode.BOTH) {
            // more efficient - create files with just the diffs
            filtContrib = determineContribFiltered(origFile, newFile);
        }

        if (evalMode == ContribEvalMode.BOTH && filtContrib.match != contrib.match) {
			LOG.error(
                "Calculated contribution {} doesn't " +
                "match calculated contribution from " +
                "filtered files {}",
                contrib,
                filtContrib
            );
        }

        // Default to full
        if (evalMode == ContribEvalMode.BOTH || evalMode == ContribEvalMode.FULL)
            return contrib;
        else
            return filtContrib;
    }

	/**
     * Determines the score differences between the supplied files,
     * by first creating filtered variants of each, containing only
     * the salient events/triggers.
	 *
	 * this saves a lot of time over doing the full eval using the
     * Perl script
     *
     * @param origFile
	 * @param newFile
	 * @return
	 */
	private EventAnswerInfo determineContribFiltered(File origFile, File newFile) {
		File filteredDir = new File(newFile.getParentFile(), "filtered");
		File filteredDirOrig = new File(filteredDir, "orig");
		File filteredDirNew = new File(filteredDir, "new");
		filteredDirOrig.mkdirs();
		filteredDirNew.mkdirs();
		File filteredOrig = new File(filteredDirOrig, origFile.getName());
		File filteredNew = new File(filteredDirNew, newFile.getName());
		try {
			writeDiffsToNewFiles(origFile, newFile, filteredOrig, filteredNew);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		EventAnswerInfo filtOrigRes = scoreFile(filteredOrig);
		EventAnswerInfo filtNewRes = scoreFile(filteredNew);
		EventAnswerInfo filtContrib = new EventAnswerInfo(filtOrigRes.answer - filtNewRes.answer, filtOrigRes.match - filtNewRes.match);
		LOG.debug("Original file (filtered) {}: {}", filteredOrig, filtOrigRes);
		LOG.debug("New file (filtered) {}: {}", filteredNew, filtNewRes);
		LOG.debug("Net contribution (filtered): {}", filtContrib);
		return filtContrib;
	}

	private EventAnswerInfo determineContribFull(File origFile, File newFile) {
		EventAnswerInfo origRes = scoreFile(origFile);
		EventAnswerInfo newRes = scoreFile(newFile);
		EventAnswerInfo contrib = new EventAnswerInfo(
            origRes.answer - newRes.answer,
            origRes.match - newRes.match
        );

        LOG.debug("Original file {}: {}", origFile, origRes);
		LOG.debug("New file {}: {}", newFile, newRes);
		LOG.debug("Net contribution: {}", contrib);

        return contrib;
	}

	private void writeDiffsToNewFiles(File file1, File file2, File filtered1, File filtered2) throws IOException {
		List<Annotation> anns1 = readAnnotationsFromFile(file1);
		List<Annotation> anns2 = readAnnotationsFromFile(file2);
		//first we need to work out annotations which are only in one file, a
		Set<Annotation> annsOnlyIn1 = new HashSet<Annotation>(anns1);
		Set<Annotation> annsOnlyIn2 = new HashSet<Annotation>(anns2);
		annsOnlyIn1.removeAll(new HashSet<Annotation>(anns2));
		annsOnlyIn2.removeAll(new HashSet<Annotation>(anns1));
		LOG.debug("Found {} annotations only in file 1 and {} only in file 2 from {} and {} originally",
				annsOnlyIn1.size(), annsOnlyIn2.size(), anns1.size(), anns2.size());
		// then we get the closure, to include other relevant annotations
		List<Annotation> annsIn1TC = transClosureOfRelevant(anns1, annsOnlyIn1);
		List<Annotation> annsIn2TC = transClosureOfRelevant(anns2, annsOnlyIn2);
		// Then we need to find those which were only added as part of the closure
		Set<Annotation> annsClosureOnly1 = new HashSet<Annotation>(annsIn1TC);
		annsClosureOnly1.removeAll(annsOnlyIn1);
		Set<Annotation> annsClosureOnly2 = new HashSet<Annotation>(annsIn2TC);
		annsClosureOnly2.removeAll(annsOnlyIn2);
		LOG.debug("After computing TC, {} annotations in file 1 ({} for closure only)", annsIn1TC.size(), annsClosureOnly1.size());
		LOG.debug("After computing TC, {} annotations in file 2 ({} for closure only)", annsIn2TC.size(), annsClosureOnly2.size());
		// Finally, in each case we have to write out:
		//  a) the annotations which are only used in the particular file
		//  b) any annotations which are added to the other trimmed file for well-formedness (the closure)
		//      since these are relevant in the evaluation.
		Set<Annotation> writeable1 = new HashSet<Annotation>(annsIn1TC);
		writeable1.addAll(annsClosureOnly2);
		Set<Annotation> writeable2 = new HashSet<Annotation>(annsIn2TC);
		writeable2.addAll(annsClosureOnly1);
		LOG.debug("Finally have {} writable annotation for file 1, and {} for file 2", writeable1.size(), writeable2.size());
		writeItems(writeable1, filtered1);
		writeItems(writeable2, filtered2);
	}

	private List<Annotation> readAnnotationsFromFile(File file1) throws IOException {
		BufferedReader reader = FileReaderUtil.initBufferedReader(file1, CharacterEncoding.UTF_8);
		Map<String, EventAnn> evtAnns = new HashMap<String, EventAnn>();
		Map<String, TriggerAnn> trigAnns = new HashMap<String, TriggerAnn>();
		String line;
		while ((line = reader.readLine()) != null) {
			if (line.startsWith("E")) {
				EventAnn ann = new EventAnn(line, evtAnns, trigAnns);
				evtAnns.put(ann.getID(), ann);
			} else if (line.startsWith("T")) {
				TriggerAnn ann = new TriggerAnn(line);
				trigAnns.put(ann.getID(), ann);
			}
		}
                reader.close();

		List<Annotation> allAnns = new ArrayList<Annotation>(trigAnns.values());
		allAnns.addAll(evtAnns.values());
		BufferedWriter rawWriter = FileWriterUtil.initBufferedWriter(new File(file1.getAbsolutePath() + ".raw"),
				CharacterEncoding.UTF_8, WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
		for (EventAnn evt : evtAnns.values())
			rawWriter.write(evt + " [" + evt.hashCode() + "]" + "\n");
		rawWriter.close();
		return allAnns;
	}

	private List<Annotation> transClosureOfRelevant(List<Annotation> allAnns, Set<Annotation> relevantAnns) throws IOException {
		Set<String> relevantIds = new HashSet<String>();
		Map<String, TriggerAnn> allTriggers = new HashMap<String, TriggerAnn>();
		Map<String, EventAnn> allEvents = new HashMap<String, EventAnn>();
		for (Annotation ann : allAnns) {
			if (ann instanceof EventAnn)
				allEvents.put(ann.getID(), (EventAnn) ann);
			else
				allTriggers.put(ann.getID(), (TriggerAnn) ann);
		}
		Set<String> pendingRelevantIds = new HashSet<String>();
		for (Annotation ann : relevantAnns)
			pendingRelevantIds.add(ann.getID());
		LOG.trace("Core relevant IDs are: {}", pendingRelevantIds);
		while (pendingRelevantIds.size() > 0) {
			Set<String> nextPendingRelevantIds = new HashSet<String>();
			for (String id : pendingRelevantIds) {
				LOG.trace("Finding needed events/triggers for {}", id);
				relevantIds.add(id);
				if (id.startsWith("E")) {
					EventAnn evt = allEvents.get(id);
					List<String> args = new ArrayList<String>();
					args.add(evt.getEventTrigger());
					args.addAll(evt.getEventThemes());
					String cause = evt.getEventCause();
					if (cause != null)
						args.add(cause);
					LOG.trace("Relevant args are: {}", args);
					for (String arg : args) {
						if (!relevantIds.contains(arg)) // don't konw about the argument; add it
							nextPendingRelevantIds.add(arg);
					}
				}
			}
			pendingRelevantIds.clear();
			pendingRelevantIds = nextPendingRelevantIds;
		}
		LOG.trace("Final list of relevant ID is {}", relevantIds);
		List<Annotation> closureAnns = new ArrayList<Annotation>();
		for (String relevId : relevantIds) {
			TriggerAnn trigger = allTriggers.get(relevId);
			if (trigger != null)
				closureAnns.add(trigger);
			EventAnn evt = allEvents.get(relevId);
			if (evt != null)
				closureAnns.add(evt);
		}
		return closureAnns;
	}


	private void writeItems(Collection<Annotation> relevantAnns, File filtered1) throws IOException {
		BufferedWriter writer = null;
		BufferedWriter rawWriter = null;
		try {
			writer = FileWriterUtil.initBufferedWriter(filtered1, CharacterEncoding.UTF_8, WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
			rawWriter = FileWriterUtil.initBufferedWriter(new File(filtered1.getAbsolutePath() + ".raw"),
					CharacterEncoding.UTF_8, WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
			for (Annotation ann : relevantAnns) {
				try {
					TriggerAnn trigger = (TriggerAnn) ann;
					writer.write(trigger.toA2String() + "\n");
					rawWriter.write(trigger + " [" + trigger.hashCode() + "]" + "\n");
				} catch (ClassCastException e) {

				}
			}
			for (Annotation ann : relevantAnns) {
				try {
					EventAnn evt = (EventAnn) ann;
					writer.write(evt.toA2String() + "\n");
					rawWriter.write(evt + " [" + evt.hashCode() + "]" + "\n");
				} catch (ClassCastException e) {

				}
			}
		} finally {
			if (writer != null)
				writer.close();
			if (rawWriter != null)
				rawWriter.close();
		}
	}


	private EventAnswerInfo scoreFile(File inputFile) {
		LOG.debug("Scoring file {}", inputFile);
		if (inputFile.length() == 0)
			return new EventAnswerInfo(0, 0); // shortcut for empty files
		String evalRes = EventExtractionEvaluator.evaluateSingle(inputFile, tuningGoldDir);
		return readResultsLines(Arrays.asList(evalRes.split("\n")));
	}

	private EventAnswerInfo readResultsLines(Collection<String> resultsLines) {
		boolean matchedCurrentResult = false;
		EventAnswerInfo res = new EventAnswerInfo(0, 0);
		for (String line : resultsLines) {
			if (line.matches("^\\s+==\\[ALL-TOTAL\\]==.+$")) {
				Matcher m = Pattern.compile("^^\\s+==\\[ALL-TOTAL\\]==\\s+(\\d+)\\s+\\(\\s+\\d+\\)\\s+([\\d#]+)\\s+\\(\\s+(\\d+)\\).+$").matcher(line);
				if (!m.find())
					throw new RuntimeException("The format of the line: " + line
							+ " is not valid. Please check.");
				int ans = m.group(2).startsWith("#") ? 10000 : Integer.parseInt(m.group(2));
				res.answer += ans;
				int matches = Integer.parseInt(m.group(3));
				res.match += matches;
				matchedCurrentResult = true;
			}
		}
		if (!matchedCurrentResult)
			throw new RuntimeException("No ALL-TOTAL lines found");
		return res;
	}

	private int countEvents(File inputFile) throws IOException {
		BufferedReader reader = FileReaderUtil.initBufferedReader(inputFile, CharacterEncoding.UTF_8);
		String line;
		int count = 0;
		while ((line = reader.readLine()) != null) {
			if (line.startsWith("E"))
				count++;
		}
                reader.close();
		return count;
	}

	protected void iterativeRuleOptimizationProcess() {
		long starting = System.currentTimeMillis();
		int iteration = 0;
		boolean quickExtractionsHandled = false;

        while(true) {
            LOG.info(
                "This is the {} time rule optimization.........",
                ++iteration
            );
			int numberofLowerPerformingRules =
                evaluateContributionOfEachRule();

            //if no lower performing rules existing, exit the loop
			if(numberofLowerPerformingRules == 0) {
				if (!quickExtractionsHandled) {
					quickExtractionsHandled = true; // we've done the short docs already; move onto the time-consuming ones
					LOG.info("Re-adding {} documents which were held out due to long extractions, and removing other docs",
							excludedDocIds.size());
					// invert the set of excluded documents, so it now has *only* the short documents
					// ie now we're optimising over hte longer documents exclusively:
					Set<String> longExtractionTimeIds = excludedDocIds;
					excludedDocIds = docProd.getIdsToAnnotatedSentences().keySet();
					excludedDocIds.removeAll(longExtractionTimeIds);
				} else {
					LOG.info("No low performing rules were found; finished optimization");
					break;
				}
			}
			System.out.println("Writing the optimized rules to folder " + optimRulesDir);
			//remove the rule folder for cleaning
			File optimRulesDirFile = new File(optimRulesDir);
			if (!optimRulesDirFile.isDirectory())
				LOG.error("'{}' is not a directory; cannot delete");
			else {
				try {
					FileUtil.deleteDirectory(optimRulesDirFile);
				} catch (NullPointerException e) {
					LOG.error("NPE while trying to delete {}", optimRulesDir);
				}
			}
            optimRulesDirFile.mkdirs(); // recreate the directory (since if there are no rules matched, it won't get created)
			//dump the resulting optimized rules to rule folder
			writeEventRulesToFiles(eventExtractor.getSimpleEventRules());
			writeEventRulesToFiles(eventExtractor.getPTMEventRules());
			writeEventRulesToFiles(eventExtractor.getComplexEventRules());
			//re-evaluating event extraction results after removing some rules
		    System.out.println("Re-Evaluating event extraction after removing "
		    		+ numberofLowerPerformingRules + " lower performing event rules........");
			eventExtractor = new EventExtraction(docProd, optimRulesDir, extractionThresholds, nProcThreads,
					eventsPerTriggerRuleSoftMax);
			if (!enableSoftTimeouts)
				eventExtractor.disableSoftTimeout();
			eventExtractor.removeDocsById(excludedDocIds);
			eventExtractor.setEventsPanicThreshold(this.eventsPanicThreshold);
			eventExtractor.setExtractionTimeout(extractionTimeout);
		    eventExtractor.eventExtractionByMatchingRulesWithSentences(PATH_TO_PREDICTED_EVENT_FOR_OPTIMIZATION);
			eventExtractor.evaluateEventPrediction(PATH_TO_EVENT_EVALUATION, tuningGoldDir);
		}
		//report the optimized performance
		long ending = System.currentTimeMillis();
		System.out.println("Finished optimization process ...........");
		System.out.print("The entire optimization process used " + iteration + " iterations and took " +
				roundDecimalPlaces((ending - starting)*1.0/60000, 2) + " minutes\n");
	}

	/**
	 * write the optimized event rules to files
	 * in terms of the event type
	 */
	private void writeEventRulesToFiles(Map<String, List<EventRule>> categorizedRules) {
		for(String eventType : categorizedRules.keySet()) {
			System.out.println("Writing " + eventType + " with " +
					categorizedRules.get(eventType).size() + " rules");
			//specify where to write
			//check the specified context depth
			File outputFile = new File(optimRulesDir, eventType + ".rule");
	    	outputFile.getParentFile().mkdirs();
	    	BufferedWriter output;
			try {
				output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8,
	                    WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
				int count = 0;
			    for(EventRule rule : categorizedRules.get(eventType)) {
			    	//if the rule is marked to remove, skip it
			    	if(!rule.getRemovalSign())
			    	    output.write( ++count + ":\t"+ rule + "\n" );
			    }
			    output.close();
			} catch (FileNotFoundException e) {
				throw new RuntimeException("Unable to open the output file: "
						+ outputFile.getAbsolutePath(), e);
			} catch (IOException e) {
				throw new RuntimeException("Unable to process the output file: ", e);
			}
		}
	}

	/**
	 * static method to round decimal values to the specified places
	 * @param valueToRound
	 * @param numberOfDecimalPlaces
	 * @return rounded decimal values
	 */
	public static double roundDecimalPlaces(double valueToRound, int numberOfDecimalPlaces) {
	    double multipicationFactor = Math.pow(10, numberOfDecimalPlaces);
	    double interestedInZeroDPs = valueToRound * multipicationFactor;
	    return Math.round(interestedInZeroDPs) / multipicationFactor;
	}

	public void disableSoftTimeout() {
		enableSoftTimeouts = false;
	}


}

class EventAnn extends gov.nih.bnst.preprocessing.annotation.Event implements Annotation {
	private static final Logger LOG = LoggerFactory.getLogger(EventRuleOptimization.class);

	private Map<String, EventAnn> allEvents;
	private Map<String, TriggerAnn> allTriggers;
	public EventAnn(String record, Map<String, EventAnn> allEvents, Map<String, TriggerAnn> trigAnns) {
		super(record);
		this.allEvents = allEvents;
		this.allTriggers = trigAnns;
	}

	private HashCode hash = null; // memoize hash value

	public EventAnn(String record) {
		super(record);
	}

	@Override
	public boolean equals(Object obj) {
		if (obj == null)
			return false;
		EventAnn other;
		try {
			other = (EventAnn) obj;
		} catch (ClassCastException e) {
			return super.equals(obj);
		}
		if (!getTriggerInstance().equals(other.getTriggerInstance()))
			return false;
		if (getEventThemes().size() != other.getEventThemes().size())
			return false;
		for (Object outerTheme : getThemeInstances()) {
			boolean matched = false;
			for (Object innerTheme : other.getThemeInstances()) {
				if (outerTheme.equals(innerTheme)) {
					matched = true;
					break;
				}
			}
			if (!matched)
				return false;
		}
		if (getCauseInstance() == null)
			return other.getCauseInstance() == null;
		else
			if (!getCauseInstance().equals(other.getCauseInstance()))
				return false;
		return true;
	}

	public Trigger getTriggerInstance() {
		return allTriggers.get(getEventTrigger());
	}

	public List<Object> getThemeInstances() {
		List<Object> themes = new ArrayList<Object>();
		for (String t : getEventThemes()) {
			if (t.startsWith("T")) {
				themes.add(t); // if it's a protein, don't need to do
										// anything as they are a fixed set
			} else {
				EventAnn evt = allEvents.get(t);
				themes.add(evt);
			}
		}
		return themes;
	}

	public Object getCauseInstance() {
		if (getEventCause() == null)
			return null;
		if (getEventCause().startsWith("T")) {
			return getEventCause();
		} else {
			return allEvents.get(getEventCause());
		}
	}

	public HashCode getGuavaHash() {
		if (hash == null) {
			HashFunction hf = Hashing.md5();
			Hasher h = hf.newHasher();
			Trigger trig = getTriggerInstance();
			h.putString(getEventCategory());
			h.putInt(trig.getStartIndex()).putInt(trig.getEndIndex());
			for (String t : getEventThemes()) {
				if (t.startsWith("T")) {
					h.putString("th:" + t); // if it's a protein, don't need to
											// do anything as they are a fixed
											// set
				} else {
					EventAnn evt = allEvents.get(t);
					h.putString("th:" + evt.getGuavaHash().toString());
				}
			}
			String cause = getEventCause();
			if (cause != null) {
				if (cause.startsWith("T")) {
					h.putString("cs:" + cause);
				} else {
					EventAnn evt = allEvents.get(cause);
					h.putString("cs:" + evt.getGuavaHash().toString());
				}
			}
			hash = h.hash();
		}
		return hash;
	}

	public String toString() {
		String themeRep = "";
		for (Object theme : getThemeInstances())
			themeRep += "(" + theme + ")";
		return String.format("%s:(%s) Themes:(%s) Cause:(%s)", getEventCategory(), getTriggerInstance(),
				themeRep, getCauseInstance());
	}

	public int hashCode() {
		return getGuavaHash().asInt();
	}

	@Override
	public String getID() {
		return getEventID();
	}
}


class TriggerAnn extends Trigger implements Annotation {
	private static final Logger LOG = LoggerFactory.getLogger(EventRuleOptimization.class);

	private HashCode hash = null;

	public TriggerAnn(String record) {
		super(record);
	}

	public HashCode getGuavaHash() {
		if (hash == null) {
			HashFunction hf = Hashing.md5();
			Hasher h = hf.newHasher();
			h.putInt(getStartIndex()).putInt(getEndIndex());
			hash = h.hash();
		}
		return hash;
	}

	public int hashCode() {
		return getGuavaHash().asInt();
	}

	@Override
	public boolean equals(Object obj) {
		if (obj == null)
			return false;
		try {
			TriggerAnn newObj = (TriggerAnn) obj;
			return getStartIndex() == newObj.getStartIndex() && getEndIndex() == newObj.getEndIndex();
		} catch (ClassCastException e) {
			return super.equals(obj);
		}
	}

	public String toString() {
		return getStartIndex() + ":" + getEndIndex();
	}

	@Override
	public String getID() {
		return getTriggerID();
	}

}

class EventAnswerInfo {
	public int answer;
	public int match;

	public EventAnswerInfo(int answer, int match) {
		this.answer = answer;
		this.match = match;
	}

	public String toString() {
		return String.format("%d answers; %d matches", answer, match);
	}
}
