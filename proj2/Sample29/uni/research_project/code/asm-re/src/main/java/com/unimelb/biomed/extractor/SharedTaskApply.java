package com.unimelb.biomed.extractor;

import gov.nih.bnst.eventextraction.EventExtraction;
import gov.nih.bnst.eventextraction.VariomeRelationExtraction;
import gov.nih.bnst.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;

import java.io.BufferedOutputStream;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.Writer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.dependency.DEPTree;
import com.googlecode.clearnlp.util.UTOutput;
import com.unimelb.biomed.extractor.annotations.AnnotatedCPDoc;
import com.unimelb.biomed.extractor.annotations.AnnotatedCPDocsFromDirectory;
import com.unimelb.biomed.extractor.annotations.AnnotatedDocCollection;
import com.unimelb.biomed.extractor.annotations.AnnotatedDocument;
import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;
import com.unimelb.biomed.extractor.learning.PatternLearner;

public class SharedTaskApply extends SharedTaskExtract {

	private static final Logger LOG = LoggerFactory.getLogger(SharedTaskApply.class);

	private EventExtraction eventExtractor;
    private VariomeRelationExtraction relationExtractor;
	private static final String parseDir = SharedTaskHelper.TEST_PARSE_DIR;
	private static final String rulesDir = SharedTaskHelper.OPTIMIZED_RULES_DIR;
	private final String testPredsDir = SharedTaskHelper.TEST_PREDICTIONS_DIR;
	private final String testEvalDir = SharedTaskHelper.TEST_EVAL_DIR;

	@Argument(index=0, required=true)
	private String testDataDir;

	public SharedTaskApply(String testDataDir) {
		this.testDataDir = testDataDir;
		init();
	}

	public SharedTaskApply(String testDataDir, Map<String, Integer> thresholds) {
		this.testDataDir = testDataDir;
		overriddenThresholds = thresholds;
		init();
	}


	public SharedTaskApply(String testDataDir, String thresholdsFileName) {
		this.testDataDir = testDataDir;
		this.thresholdsFileName = thresholdsFileName;
		init();
	}

	public SharedTaskApply(String testDataDir, boolean zeroThresholds) {
		this.testDataDir = testDataDir;
		this.zeroThresholds = zeroThresholds;
		init();
	}


	public SharedTaskApply(String[] cliArgs) {
		readArgs(cliArgs);
		init();
	}

	protected void apply() throws IOException {
        LOG.trace("Initializing document producer using corpus {}", corpus);
        DocumentProducer docProd = getDocProducer(parseDir, testDataDir, corpus, false);
        new File(testPredsDir).mkdir();
        if (corpus.equals("genia")) {
            eventExtractor = new EventExtraction(
                docProd,
                rulesDir,
                overriddenThresholds,
                procThreads,
                eventsPerTriggerRuleSoftMax
            );
            if (noSoftTimeout)
    			eventExtractor.disableSoftTimeout();
    		eventExtractor.setEventsPanicThreshold(eventsPanicThreshold);
    		eventExtractor.eventExtractionByMatchingRulesWithSentences(testPredsDir);
    		String results = eventExtractor.evaluateEventPrediction(testEvalDir, testDataDir);
    		writeResults(results);
        }
        else if (corpus.equals("variome")) {
            relationExtractor = new VariomeRelationExtraction(
                docProd,
                rulesDir,
                overriddenThresholds,
                procThreads,
    			eventsPerTriggerRuleSoftMax
            );
            if (noSoftTimeout)
    			relationExtractor.disableSoftTimeout();
    		relationExtractor.setRelationsPanicThreshold(eventsPanicThreshold);
            relationExtractor.relationExtractionByMatchingRulesWithSentences(
                testPredsDir,
                relationType
            );

            String results = relationExtractor.evaluateRelationPrediction(
                testEvalDir, testDataDir, rulesDir
            );
    		writeResults(results);
        }
        else if (corpus.equals("seedev")) {
            eventExtractor = new EventExtraction(
                docProd,
                rulesDir,
                overriddenThresholds,
                procThreads,
                eventsPerTriggerRuleSoftMax
            );
            if (noSoftTimeout)
    			eventExtractor.disableSoftTimeout();
    		eventExtractor.setEventsPanicThreshold(eventsPanicThreshold);
    		eventExtractor.eventExtractionByMatchingRulesWithSentences(testPredsDir);
    		String results = eventExtractor.evaluateEventPrediction(testEvalDir, testDataDir);
    		writeResults(results);
        }
        else {
            System.out.println("ERROR: Unknown corpus - " + corpus);
            System.exit(0);
        }

	}

	public int getProcThreads() {
		return procThreads;
	}

	public void setProcThreads(int procThreads) {
		this.procThreads = procThreads;
	}

	private void writeResults(String results) throws IOException {
		OutputStream resOs = new FileOutputStream(SharedTaskHelper.TEST_RESULTS_FILE);
		Writer out = new BufferedWriter(new OutputStreamWriter(resOs));
		out.write(results);
		out.close();
	}

	public static void main(String[] args) {
		SharedTaskApply stApply = new SharedTaskApply(args);
		try {
			stApply.apply();
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}
 }
