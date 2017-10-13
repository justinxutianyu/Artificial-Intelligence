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

import gov.nih.bnst.patternlearning.RelationRule;
import gov.nih.bnst.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst.preprocessing.annotation.Trigger;
import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileReaderUtil;
import edu.ucdenver.ccp.common.file.FileUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import gov.nih.bnst.eventextraction.Relation;
import gov.nih.bnst.eventextraction.VariomeRelationExtraction;
import gov.nih.bnst.eventextraction.VariomeRelationExtractionEvaluator;

public class RelationRuleOptimization {

	private static final Logger LOG = LoggerFactory.getLogger(RelationRuleOptimization.class);

	/** relation extraction class object */
	VariomeRelationExtraction relationExtractor;

	/** path to the predicted relation evaluation directory */
	private static final String PATH_TO_RELATION_EVALUATION = SharedTaskHelper.TUNING_EVAL_DIR;

	/** path to the predicted relation directory for optimization */
	private static final String PATH_TO_PREDICTED_RELATION_FOR_OPTIMIZATION = SharedTaskHelper.TUNING_PREDICTIONS_DIR;

	/** path to write the optimized relation rules */
	private final String optimRulesDir;

	/** rule optimization accuracy threshold */
	private double ruleAccuracyThreshold = 0.0;

	/** relation types */
	String[] relationTypes = {
        "has",
        "relatedTo"
    };

	/**
     * The document producer for the tuning (optimization)
     * documents - which could be the same as the dev set
     */
	private DocumentProducer docProd;

	/** The thresholds for the relation extraction */
	private Map<String, Integer> extractionThresholds;

	/** The path to the gold .a1/.a2 annotations for the tuning files */
	private final String tuningGoldDir;

	/** the number of threads to use in relation extraction */
	private int nProcThreads = 1;

	/**
     * The threshold at which we stop extracting relations
     * because we're wildly overgenerating
     */
	private int relationsPanicThreshold = 2000;

	/** (DEPRECATED) passed through to relation extraction; only get around this
	 * many rule matches per trigger, to try and stop over-generation
	 *
	 * -1 (the default) is unbounded; any subgraph matches (within the subgraph match tolerance)
	 * will be used
	 */
	private int relationsPerTriggerRuleSoftMax = -1;

	private final String rawRulesDir;

	private final AtomicInteger numberofLowerPerformingRules =
        new AtomicInteger();

	/**
     * Don't allow relation extraction for a single
     * document to take longer than this
     */
	private int extractionTimeout = -1;

	private Set<String> excludedDocIds;

	public enum ContribEvalMode {
		FULL,
		FILTERED,
		BOTH
	}

	private ContribEvalMode evalMode = ContribEvalMode.FILTERED;

	private boolean enableSoftTimeouts = true;

    //The relation type to optimize for
    private String relationType = "";

	/**
	 * Constructor to start the initial evaluation based on the original rule set
	 * @param docProd - the source of the documents to optimize over
	 * @param rawRulesDir - the original unmodified rule directory
	 * @param optimRulesDir - the directory where the newly optimized rules should be written
	 * @param tuningGoldDir - the directory with the gold data for the tuning documents in `docProd`
	 * @throws IOException - if the optimized rules directory cannot be created
	 */
	public RelationRuleOptimization (
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

    public RelationRuleOptimization(
        DocumentProducer docProd,
        String rawRulesDir,
		String optimRulesDir,
        String tuningGoldDir
    ) {
		this(
            docProd,
            rawRulesDir,
            optimRulesDir,
            tuningGoldDir,
            new HashMap<String, Integer>(0),
            1
        );
	}

	/**
     * Specify a new threshold (instead of the default 2000) at which to
	 * give up relation extraction
	 * @param thresh
	 */
	public void setRelationsPanicThreshold(int thresh) {
		relationsPanicThreshold = thresh;
	}

	public void setExtractionTimeout(int timeout) {
		extractionTimeout  = timeout;
	}

	/** specify a new target accuracy threshold which we optimize towards,
	 * instead of the default 0.25 */
	public void setRuleAccuracyThreshold(double newThresh) {
		ruleAccuracyThreshold = newThresh;
	}

    public void setRelationType(String relationType) {
        this.relationType = relationType;
    }

	public void optimize() {
		LOG.info(
            "In optimization, soft timeouts are {}",
            enableSoftTimeouts ? "ENABLED" : "DISABLED"
        );
		startOptimization();
        //iterativeRuleOptimizationProcess();
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

        //Set up the relation extractor for the first run
        /*
        relationExtractor = new VariomeRelationExtraction(
            this.docProd,
            this.optimRulesDir,
            this.extractionThresholds,
            this.nProcThreads,
			this.relationsPerTriggerRuleSoftMax
        );
		if (!enableSoftTimeouts)
			relationExtractor.disableSoftTimeout();
		relationExtractor.setRelationsPanicThreshold(this.relationsPanicThreshold);
		relationExtractor.setExtractionTimeout(extractionTimeout);

        //Extract and evaluate a set of relations
        relationExtractor.relationExtractionByMatchingRulesWithSentences(
            PATH_TO_PREDICTED_RELATION_FOR_OPTIMIZATION,
            relationType
        );
		relationExtractor.evaluateRelationPrediction(
            PATH_TO_RELATION_EVALUATION,
            this.tuningGoldDir,
            this.rawRulesDir
        );

        //Store docs with long extraction times and leave them until later
		excludedDocIds = relationExtractor.docIdsWithLongExtractionTimes(15000);
		LOG.info(
            "Temporarily removing {} documents with " +
            "extraction times of 15 seconds or more: {}",
			excludedDocIds.size(),
            excludedDocIds
        );
        */
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
			writeRelationRulesToFiles(relationExtractor.getRelationRules());
			//re-evaluating relation extraction results after removing some rules
		    System.out.println("Re-Evaluating relation extraction after removing "
		    		+ numberofLowerPerformingRules + " lower performing relation rules........");
			relationExtractor = new VariomeRelationExtraction(docProd, optimRulesDir, extractionThresholds, nProcThreads,
					relationsPerTriggerRuleSoftMax);
			if (!enableSoftTimeouts)
				relationExtractor.disableSoftTimeout();
			relationExtractor.removeDocsById(excludedDocIds);
			relationExtractor.setRelationsPanicThreshold(this.relationsPanicThreshold);
			relationExtractor.setExtractionTimeout(extractionTimeout);
		    relationExtractor.relationExtractionByMatchingRulesWithSentences(
                PATH_TO_PREDICTED_RELATION_FOR_OPTIMIZATION,
                relationType
            );
			relationExtractor.evaluateRelationPrediction(PATH_TO_RELATION_EVALUATION, tuningGoldDir, rawRulesDir);
		}
		//report the optimized performance
		long ending = System.currentTimeMillis();
		System.out.println("Finished optimization process ...........");
		System.out.print("The entire optimization process used " + iteration + " iterations and took " +
				roundDecimalPlaces((ending - starting)*1.0/60000, 2) + " minutes\n");
	}

	public int evaluateContributionOfEachRule() {
        //Ranking(optimization) results for each rule
		numberofLowerPerformingRules.set(0);

        //Structure to store
        //relationType->relationRule->impactedDocument
        //relationship for relation rule optimization
		Map<String, Map<RelationRule, Set<String>>> ruleTypeToRuleToImpactedDocuments =
            relationExtractor.getRuleToDocumentsMap();

        if (ruleTypeToRuleToImpactedDocuments.size() == 0)
			LOG.error("No rules to document mapping found");

        //Structure to store document->relations relationship for relation rule
        //optimization
		final Map<String, List<Set<Relation>>> documentToRelations =
            relationExtractor.getDocumentToRelationsMap();

        //Assess the quality of each rule when applied to the documents
        //it has been matched to
		for (String category : ruleTypeToRuleToImpactedDocuments.keySet()) {
            //Mapping from rule -> docs, indicating which rules have
            //been matched to what docs.
            final Map<RelationRule, Set<String>> categoryImpactedDocs =
                ruleTypeToRuleToImpactedDocuments.get(category);

            //The set of rules from the mapping above
            Set<RelationRule> rules = categoryImpactedDocs.keySet();

            //Main rule evaluation loop: evaluates each of the rules
            //from the set above against the documents in which
            //it has been detected.
            for (RelationRule rule : rules) {
				evaluateSingleRule(
                    rule,
                    categoryImpactedDocs,
                    documentToRelations
                );
            }
        }
	    return numberofLowerPerformingRules.get();
	}

	protected void evaluateSingleRule (
        RelationRule rule,
        Map<RelationRule, Set<String>> categoryImpactedDocs,
		Map<String, List<Set<Relation>>> documentToRelations
    ) {
		long startTime = System.currentTimeMillis();
		int currentAnswer = 0;
        int currentMatch = 0;
		String uniqueSubDir = rule.getRelationCategory() + "-" + rule.getRuleID();

         //Init optimization and evaluation directories
         //Note each directory is unique, to avoid clashes
         //between threads.
		File optimDir = new File(
            PATH_TO_PREDICTED_RELATION_FOR_OPTIMIZATION,
			uniqueSubDir
        );
		File evalDir = new File(
            PATH_TO_RELATION_EVALUATION,
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
        //This mimics the extraction of relations for a single document
        //in the VariomeRelationExtraction class.
        for(String pmid : categoryImpactedDocs.get(rule)) {
			LOG.debug(
                "Checking impacted document {} for rule {}",
                pmid,
                rule.getRuleID()
            );

            LOG.debug(
                "This document as relations: {}",
                documentToRelations.get(pmid)
            );

			//Create a file for the prediction
			File outputFile = new File(optimDir, pmid + ".ann");
			outputFile
                .getParentFile()
                .mkdirs();

            //Initial conditions for relation prediction
            int relationStartingID = 1;
			List<String> documentRelationList = new ArrayList<String>();

            //Loop over each set of relations detected in this document
            for(Set<Relation> set : documentToRelations.get(pmid)) {
				Set<Relation> updatedRelationSet = new HashSet<Relation>();

                //If this relation isn't the same as the relation
                //linked to the rule we're evaluating, create a new
                //relation using the original rule stored with the
                //relation.
                for(Relation relation : set) {
					if(!relation.getOriginalRelationRule().equals(rule)) {
						Relation newRelation =
                            new Relation(relation.getOriginalRelationRule());
						newRelation.update(relation);
						updatedRelationSet.add(newRelation);
					}
				}

                //If our updated set of relations isn't empty, post-process
                //relations and generate ANN strings.
				if(!updatedRelationSet.isEmpty()) {
			    	//Postprocess raw relations
					updatedRelationSet =
                        relationExtractor.postprocessRawExtractedRelations(
                            updatedRelationSet
                        );

                    //Convert postprocessed raw relations to ANN format
					Integer[] currentIDs = relationExtractor.rawRelationsToANNStrings(
                        updatedRelationSet,
                        relationStartingID,
                        documentRelationList
                    );
			    	relationStartingID = currentIDs[0];
			    }
			} //End relation set processing loop

            //Write predictions to output file
			BufferedWriter output;
			try {
				output = FileWriterUtil.initBufferedWriter(
                    outputFile,
                    CharacterEncoding.UTF_8,
					WriteMode.OVERWRITE,
                    FileSuffixEnforcement.OFF
                );

                for (String relation : documentRelationList)
					output.write(relation + "\n");

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
            if (!inputFile.isFile() || !inputFile.getName().matches("^\\S+\\.ann$"))
				continue;

            //Determine the contribution of this file
			RelationAnswerInfo contribInfo = determineContribution(
				new File(
                    PATH_TO_PREDICTED_RELATION_FOR_OPTIMIZATION,
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


	private RelationAnswerInfo determineContribution(File origFile, File newFile) {
		RelationAnswerInfo contrib = null;
        RelationAnswerInfo filtContrib = null;

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
     * the salient relations/triggers.
	 *
	 * this saves a lot of time over doing the full eval using the
     * Perl script
     *
     * @param origFile
	 * @param newFile
	 * @return
	 */
	private RelationAnswerInfo determineContribFiltered(File origFile, File newFile) {
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
		RelationAnswerInfo filtOrigRes = scoreFile(filteredOrig);
		RelationAnswerInfo filtNewRes = scoreFile(filteredNew);
		RelationAnswerInfo filtContrib = new RelationAnswerInfo(filtOrigRes.answer - filtNewRes.answer, filtOrigRes.match - filtNewRes.match);
		LOG.debug("Original file (filtered) {}: {}", filteredOrig, filtOrigRes);
		LOG.debug("New file (filtered) {}: {}", filteredNew, filtNewRes);
		LOG.debug("Net contribution (filtered): {}", filtContrib);
		return filtContrib;
	}

	private RelationAnswerInfo determineContribFull(File origFile, File newFile) {
		RelationAnswerInfo origRes = scoreFile(origFile);
		RelationAnswerInfo newRes = scoreFile(newFile);
		RelationAnswerInfo contrib = new RelationAnswerInfo(
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
		Map<String, RelationAnn> relationAnns = new HashMap<String, RelationAnn>();
		String line;
		while ((line = reader.readLine()) != null) {
			if (line.startsWith("R")) {
				RelationAnn ann = new RelationAnn(line, relationAnns);
				relationAnns.put(ann.getID(), ann);
			}
		}
        reader.close();

		List<Annotation> allAnns =
            new ArrayList<Annotation>(relationAnns.values());
		BufferedWriter rawWriter = FileWriterUtil
            .initBufferedWriter(
                new File(file1.getAbsolutePath() + ".raw"),
				CharacterEncoding.UTF_8,
                WriteMode.OVERWRITE,
                FileSuffixEnforcement.OFF
            );

        for (RelationAnn relation : relationAnns.values())
			rawWriter.write(relation + " [" + relation.hashCode() + "]" + "\n");
		rawWriter.close();
		return allAnns;
	}

	private List<Annotation> transClosureOfRelevant(List<Annotation> allAnns, Set<Annotation> relevantAnns) throws IOException {
		Set<String> relevantIds = new HashSet<String>();
		Map<String, TriggerAnn> allTriggers = new HashMap<String, TriggerAnn>();
		Map<String, RelationAnn> allRelations = new HashMap<String, RelationAnn>();
		for (Annotation ann : allAnns) {
			if (ann instanceof RelationAnn)
				allRelations.put(ann.getID(), (RelationAnn) ann);
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
				LOG.trace("Finding needed relations/triggers for {}", id);
				relevantIds.add(id);
				if (id.startsWith("R")) {
					RelationAnn relation = allRelations.get(id);
					List<String> args = new ArrayList<String>();
					args.addAll(relation.getRelationThemes());
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
			RelationAnn relation = allRelations.get(relevId);
			if (relation != null)
				closureAnns.add(relation);
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
					RelationAnn relation = (RelationAnn) ann;
					writer.write(relation.toANNString() + "\n");
					rawWriter.write(relation + " [" + relation.hashCode() + "]" + "\n");
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


	private RelationAnswerInfo scoreFile(File inputFile) {
		LOG.debug("Scoring file {}", inputFile);
		if (inputFile.length() == 0)
			return new RelationAnswerInfo(0, 0); // shortcut for empty files
		String evalRes = VariomeRelationExtractionEvaluator.evaluateSingle(inputFile, tuningGoldDir, rawRulesDir);
		return readResultsLines(Arrays.asList(evalRes.split("\n")));
	}

	private RelationAnswerInfo readResultsLines(Collection<String> resultsLines) {
		boolean matchedCurrentResult = false;
		RelationAnswerInfo res = new RelationAnswerInfo(0, 0);
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

	private int countRelations(File inputFile) throws IOException {
		BufferedReader reader = FileReaderUtil.initBufferedReader(inputFile, CharacterEncoding.UTF_8);
		String line;
		int count = 0;
		while ((line = reader.readLine()) != null) {
			if (line.startsWith("R"))
				count++;
		}
                reader.close();
		return count;
	}

	/**
	 * write the optimized relation rules to files
	 * in terms of the relation type
	 */
	private void writeRelationRulesToFiles(Map<String, List<RelationRule>> categorizedRules) {
		for(String relationType : categorizedRules.keySet()) {
			System.out.println("Writing " + relationType + " with " +
					categorizedRules.get(relationType).size() + " rules");
			//specify where to write
			//check the specified context depth
			File outputFile = new File(optimRulesDir, relationType + ".rule");
	    	outputFile.getParentFile().mkdirs();
	    	BufferedWriter output;
			try {
				output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8,
	                    WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
				int count = 0;
			    for(RelationRule rule : categorizedRules.get(relationType)) {
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

class RelationAnn extends gov.nih.bnst.preprocessing.annotation.Relation implements Annotation {
	private static final Logger LOG = LoggerFactory.getLogger(RelationRuleOptimization.class);

	private Map<String, RelationAnn> allRelations;

	public RelationAnn(String record, Map<String, RelationAnn> allRelations) {
		super(record);
		this.allRelations = allRelations;
	}

	private HashCode hash = null; // memoize hash value

	public RelationAnn(String record) {
		super(record);
	}

	@Override
	public boolean equals(Object obj) {
		if (obj == null)
			return false;
		RelationAnn other;
		try {
			other = (RelationAnn) obj;
		} catch (ClassCastException e) {
			return super.equals(obj);
		}
		if (getRelationThemes().size() != other.getRelationThemes().size())
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
		return true;
	}

	public List<Object> getThemeInstances() {
		List<Object> themes = new ArrayList<Object>();
		for (String t : getRelationThemes()) {
			if (t.startsWith("T")) {
				themes.add(t);
			}
		}
		return themes;
	}

	public HashCode getGuavaHash() {
		if (hash == null) {
			HashFunction hf = Hashing.md5();
			Hasher h = hf.newHasher();
			h.putString(getRelationCategory());
			for (String t : getRelationThemes()) {
				if (t.startsWith("T")) {
					h.putString("th:" + t);
				}
			}
			hash = h.hash();
		}
		return hash;
	}

	public String toString() {
        String representation = getRelationCategory();
        int i = 1;
        for (String theme : getRelationThemes()) {
            representation += " Arg" + i + theme;
            i += 1;
        }
        return representation;
    }

	public int hashCode() {
		return getGuavaHash().asInt();
	}

	@Override
	public String getID() {
		return getRelationID();
	}
}

class RelationAnswerInfo {
	public int answer;
	public int match;

	public RelationAnswerInfo(int answer, int match) {
		this.answer = answer;
		this.match = match;
	}

	public String toString() {
		return String.format("%d answers; %d matches", answer, match);
	}
}
