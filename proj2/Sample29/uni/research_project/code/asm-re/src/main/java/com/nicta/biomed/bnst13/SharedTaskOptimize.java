package com.nicta.biomed.bnst13;

import gov.nih.bnst13.eventruleoptimization.EventRuleOptimization;
import gov.nih.bnst13.preprocessing.annotation.DocumentProducer;

import java.io.File;
import java.io.IOException;
import java.util.Map;

import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.nicta.biomed.bnst13.annotations.AnnotatedCPDocsFromDirectory;
import com.nicta.biomed.bnst13.annotations.AnnotatedDocCollection;
import com.nicta.biomed.bnst13.annotations.BnstRuntimeException;

public class SharedTaskOptimize extends SharedTaskExtract {
	private static final Logger LOG = LoggerFactory.getLogger(SharedTaskOptimize.class);

	private EventRuleOptimization optim;
	private static final String parseDir = SharedTaskHelper.TUNING_PARSE_DIR;
	private static final String rawRulesDir = SharedTaskHelper.LEARNED_RAW_RULES_DIR;
	private static final String testPredsDir = SharedTaskHelper.TEST_PREDICTIONS_DIR;
	private static final String optimRulesDir = SharedTaskHelper.OPTIMIZED_RULES_DIR;

	@Option(name="-a", aliases="--rule-acc-thresh", usage="Set a new target accuracy threshold below which the" +
			"rule will be discarded")
	private double ruleAccThresh = 0.25;
	
	@Option(name="--hard-timeout", usage="Time (in seconds) after which event extraction for a document is savagely abandoned;" +
			" defaults to -1, meaning no timeout (although there are internal timeouts as well)")
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
		DocumentProducer docProd = getDocProducer(parseDir, tuningGoldDataDir, false);
		new File(testPredsDir).mkdir();
		optim = new EventRuleOptimization(docProd, rawRulesDir, optimRulesDir, 
				tuningGoldDataDir, overriddenThresholds, procThreads);
		optim.setEventsPanicThreshold(eventsPanicThreshold);
		optim.setExtractionTimeout(timeout);
		optim.setRuleAccuracyThreshold(ruleAccThresh);
		if (noSoftTimeout) {
			LOG.info("--no-soft-timeout flag is set");
			optim.disableSoftTimeout();
		}
		optim.optimize();
	}

	public static void main(String[] args) {
		SharedTaskOptimize stOpt = new SharedTaskOptimize(args);
		stOpt.apply();
	}
	
 }
