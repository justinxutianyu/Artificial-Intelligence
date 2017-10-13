package com.unimelb.biomed.extractor;

import gov.nih.bnst.eventruleoptimization.EventRuleOptimization;
import gov.nih.bnst.eventruleoptimization.RelationRuleOptimization;
import gov.nih.bnst.preprocessing.annotation.DocumentProducer;

import java.io.File;
import java.io.IOException;
import java.util.Map;

import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.annotations.AnnotatedCPDocsFromDirectory;
import com.unimelb.biomed.extractor.annotations.AnnotatedDocCollection;
import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;

public class SharedTaskOptimize extends SharedTaskExtract {
	private static final Logger LOG = LoggerFactory.getLogger(SharedTaskOptimize.class);

	private EventRuleOptimization eventOptimizer;
    private RelationRuleOptimization relationOptimizer;
	private static final String parseDir = SharedTaskHelper.TUNING_PARSE_DIR;
	private static final String rawRulesDir = SharedTaskHelper.LEARNED_RAW_RULES_DIR;
	private static final String testPredsDir = SharedTaskHelper.TEST_PREDICTIONS_DIR;
	private static final String optimRulesDir = SharedTaskHelper.OPTIMIZED_RULES_DIR;

	@Option(
        name = "-a",
        aliases = "--rule-acc-thresh",
        usage = "Set a new target accuracy " +
                "threshold below which the rule " +
                "will be discarded"
    )
	private double ruleAccThresh = 0.25;

	@Option(
        name = "--hard-timeout",
        usage = "Time (in seconds) after which event " +
                "extraction for a document is savagely abandoned; " +
			    "defaults to -1, meaning no timeout " +
                "(although there are internal timeouts as well)"
    )
	private int timeout = -1;

	@Argument(index=0, required=true)
	private String tuningGoldDataDir;

	public SharedTaskOptimize(String tuningGoldDataDir) {
		this.tuningGoldDataDir = tuningGoldDataDir;
		init();
	}

	public SharedTaskOptimize(String tuningGoldDataDir, Map<String, Integer> thresholds) {
		this.tuningGoldDataDir = tuningGoldDataDir;
		overriddenThresholds = thresholds;
		init();
	}

	public SharedTaskOptimize(String tuningGoldDataDir, String thresholdsFileName) {
		this.tuningGoldDataDir = tuningGoldDataDir;
		this.thresholdsFileName = thresholdsFileName;
		init();
	}

	public SharedTaskOptimize(String tuningGoldDataDir, boolean zeroThresholds) {
		this.tuningGoldDataDir = tuningGoldDataDir;
		this.zeroThresholds = zeroThresholds;
		init();
	}

	public SharedTaskOptimize(String[] cliArgs) {
		readArgs(cliArgs);
		init();
	}


	protected void apply() {
        LOG.trace("Initializing document producer using corpus {}", corpus);
        DocumentProducer docProd = getDocProducer(
            parseDir,
            tuningGoldDataDir,
            corpus,
            false
        );

        new File(testPredsDir).mkdir();

        if (corpus.equals("genia")) {
            eventOptimizer = new EventRuleOptimization(
                docProd,
                rawRulesDir,
                optimRulesDir,
    			tuningGoldDataDir,
                overriddenThresholds,
                procThreads
            );
            eventOptimizer.setEventsPanicThreshold(eventsPanicThreshold);
    		eventOptimizer.setExtractionTimeout(timeout);
    		eventOptimizer.setRuleAccuracyThreshold(ruleAccThresh);
    		if (noSoftTimeout) {
    			LOG.info("--no-soft-timeout flag is set");
    			eventOptimizer.disableSoftTimeout();
    		}

            eventOptimizer.optimize();
        }
        else if (corpus.equals("variome")) {
            relationOptimizer = new RelationRuleOptimization(
                docProd,
                rawRulesDir,
                optimRulesDir,
                tuningGoldDataDir,
                overriddenThresholds,
                procThreads
            );
            relationOptimizer.setRelationsPanicThreshold(eventsPanicThreshold);
    		relationOptimizer.setExtractionTimeout(timeout);
    	    relationOptimizer.setRuleAccuracyThreshold(ruleAccThresh);
            relationOptimizer.setRelationType(relationType);
            if (noSoftTimeout) {
    			LOG.info("--no-soft-timeout flag is set");
    			relationOptimizer.disableSoftTimeout();
    		}

            relationOptimizer.optimize();
        }
        else {
            System.out.println("ERROR: Unknown corpus - " + corpus);
            System.exit(0);
        }
	}

	public static void main(String[] args) {
		SharedTaskOptimize stOpt = new SharedTaskOptimize(args);
		stOpt.apply();
	}

 }
