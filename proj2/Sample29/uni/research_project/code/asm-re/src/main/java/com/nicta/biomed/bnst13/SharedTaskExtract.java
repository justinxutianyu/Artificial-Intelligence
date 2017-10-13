package com.nicta.biomed.bnst13;

import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;

import gov.nih.bnst13.eventextraction.EventExtraction;

import org.kohsuke.args4j.Option;


class SharedTaskExtract extends SharedTaskRunBase {
	protected Map<String, Integer> overriddenThresholds = new HashMap<String, Integer>(10);
	@Option(name = "-t", aliases = { "--thresholds" }, usage = "Specify a file with thresholds by event type "
			+ " (overriding any zeroed thresholds) in Java Properties format. If not set, hardcoded defaults will be used")
	protected String thresholdsFileName = "";

	@Option(name = "-z", aliases = { "--zero-thresholds" }, usage = "Set tolerance threholds to for graph matching to zero")
	protected boolean zeroThresholds = false;
	
	@Option(name = "-n", aliases = {"--num-threads"}, usage="Use this many threads for event extraction")
	protected int procThreads = 1;

	@Option(name = "--ee-panic-thresh", usage="Abandon extraction when this many "
		+ " events have been found (default: 2000)")
	protected int eventsPanicThreshold = 2000;
	
	@Option(name = "-m", aliases = {"--max-events-per-trigger-rule"}, usage = "The maximum number of events " +
			"allowed for a given rule applied to a given trigger. Sets a distance  threshold which cuts " +
			"off the number of matches at this value as closely as possible")
	protected int eventsPerTriggerRuleSoftMax = -1;

	@Option(name = "--no-soft-timeout", usage = "Disable per-document timeouts in event extraction")
	protected boolean noSoftTimeout = false;

	public SharedTaskExtract() {
		super();
	}
	
	protected void init()  {
		super.init();
		if (zeroThresholds) {
			for (String evType : EventExtraction.DEFAULT_THRESHOLDS.keySet())
				overriddenThresholds.put(evType, 0);
		}
		if (!thresholdsFileName.isEmpty()) {
			Properties threshProps = readProperties(thresholdsFileName);
			for (Entry<Object, Object> tp : threshProps.entrySet())
				overriddenThresholds.put((String) tp.getKey(), Integer.parseInt((String) tp.getValue()));
		}
	}

}
