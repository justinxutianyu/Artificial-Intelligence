package gov.nih.bnst13.patternlearning;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
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

import edu.ucdenver.ccp.esm.ESM;
import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileReaderUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import edu.ucdenver.ccp.nlp.biolemmatizer.BioLemmatizer;

public class RuleFileMerger {
	
	private static final Logger LOG = LoggerFactory.getLogger(RuleFileMerger.class);
	
	/** merges two rule files, removing newly-introduced isomorphism */
	
	@Argument
	private List<String> ruleFiles = new ArrayList<String>();
	
	/** path to the new rule */
	@Option(name="-o", aliases="--output-dir", required=true)
	private String outputDir = "merged-rules";
	
	/** rule category name */
	private String category = "";

	/** store all extracted event rules */
	Map<String, List<EventRule>> allEventRules = new HashMap<String, List<EventRule>>();

	/** store extracted event rules without isomorphic rules */
	Map<String, List<EventRule>> eventRulesWithoutIsomorphism = new HashMap<String, List<EventRule>>();

	public RuleFileMerger(List<String> ruleFiles, String outputDir) {
		this.ruleFiles = ruleFiles;
		this.outputDir = outputDir;
	}
	
	public RuleFileMerger(String[] args) {
		readArgs(args);
	}
	
	protected void run() {
		List<EventRule> finalRuleList = new ArrayList<EventRule>();
		for (String ruleFileName : ruleFiles) {
			List<EventRule> rules = readRuleFile(ruleFileName);
			finalRuleList.addAll(rules);
		}
		allEventRules.put(category, finalRuleList);
		removeIsomorphicPaths();
		writeEventRulesToFiles();
	}

	/**
	 * 
	 * @param input
	 * @return
	 */
	private List<EventRule> readRuleFile(String fileName) {
		File inputFile = new File(fileName);
		if (!inputFile.isFile() || !inputFile.getName().split("\\.")[1].equals("rule"))
			throw new RuntimeException("The rule file name: " + inputFile.getName()
					+ " is not valid. Please check.");
		BufferedReader input;
		try {
			input = FileReaderUtil.initBufferedReader(inputFile, CharacterEncoding.UTF_8);
		} catch (FileNotFoundException e) {
			throw new RuntimeException("Unable to open the input file: " + inputFile.getName(), e);
		}
		if (category.isEmpty())
			category = inputFile.getName().split("\\.")[0];
		else if (!category.equals(inputFile.getName().split("\\.")[0])) {
			throw new RuntimeException("The category of two rule files are different: " + category
					+ " " + inputFile.getName().split("\\.")[0]);
		}
		List<EventRule> rules = new ArrayList<EventRule>();
		String line = null;
		try {
			while ((line = input.readLine()) != null) {
				if (line.trim().length() == 0)
					continue;
				line = line.trim();
				try {
					EventRule rule = new EventRule(line, category);
					rules.add(rule);
				} catch (RuleParsingException e) {
					LOG.error("Ignoring ill-formed rule {}: {}", line, e);
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
	 * remove isomorphic paths for each event type using ESM
	 */
	private void removeIsomorphicPaths() {
		for (String eventType : allEventRules.keySet()) {
			LOG.info("Have {} rules before removing isomorphism", allEventRules.get(eventType).size());
			// deal with isomorphic dependency graphs of event rules
			// first pairwise scan to set removal sign
			List<EventRule> evtRules = allEventRules.get(eventType);
			for (int i = 0; i < evtRules.size() - 1; i++) {
				// no need to attempt the path with removal sign true, for
				// efficiency
				if (evtRules.get(i).getRemovalSign())
					continue;
				for (int j = i + 1; j < evtRules.size(); j++) {
					// no need to attempt the path with removal sign true, for
					// efficiency
					if (evtRules.get(j).getRemovalSign())
						continue;
					// make sure when PTM and regulation-related events are
					// compared, they have same number of arguments
					if (!((evtRules.get(i).hasTheme() == allEventRules.get(eventType).get(j)
							.hasTheme()) && (evtRules.get(i).hasCause() == evtRules.get(j)
							.hasCause())))
						continue;
					// if path i's length is equal to path j's
					if (evtRules.get(i).getGraph().getVertexCount() == 
							evtRules.get(j).getGraph().getVertexCount()) {
						ESM esm = new ESM(evtRules.get(i).getGraph(),
								evtRules.get(j).getGraph());
						// set removal sign true for the isomorphic path
						if (esm.isGraphIsomorphism()) {
							evtRules.get(j).setRemovalSign(true);
							LOG.debug("graphs isomorphic: [{}] {} and [{}] {}", 
									i, evtRules.get(i), j, evtRules.get(j));
						}
					}
				}
			}
			// second scan to present paths with removal sign false
			for (int i = 0; i < evtRules.size(); i++) {
				if (!evtRules.get(i).getRemovalSign()) {
					if (eventRulesWithoutIsomorphism.containsKey(eventType)) {
						eventRulesWithoutIsomorphism.get(eventType).add(
								evtRules.get(i));
					} else {
						List<EventRule> temp = new ArrayList<EventRule>();
						temp.add(evtRules.get(i));
						eventRulesWithoutIsomorphism.put(eventType, temp);
					}
				}
			}
			
			LOG.info("There are {} rules remaining after removing isomorphism", eventRulesWithoutIsomorphism.get(eventType).size());
		}
	}

	/**
	 * write the extracted event rules to files in terms of the event type
	 */
	private void writeEventRulesToFiles() {
		for (String eventType : eventRulesWithoutIsomorphism.keySet()) {
			LOG.info("Writing " + eventType + " with "
					+ eventRulesWithoutIsomorphism.get(eventType).size() + " rules");
			// specify where to write
			// check the specified context depth
			File outputFile = new File(outputDir, eventType + ".rule");
			outputFile.getParentFile().mkdirs();
			BufferedWriter output;
			try {
				output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8,
						WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
				int count = 0;
				for (EventRule rule : eventRulesWithoutIsomorphism.get(eventType)) {
					// void the existing rule ID
					rule.setRuleID(null);
					output.write(++count + ":\t" + rule + "\n");
				}
				output.close();
			} catch (FileNotFoundException e) {
				throw new RuntimeException("Unable to open the output file: " + outputFile.getAbsolutePath(), e);
			} catch (IOException e) {
				throw new RuntimeException("Unable to process the output file: ", e);
			}
		}
	}
	
	protected void readArgs(String[] cliArgs) {
		CmdLineParser parser = new CmdLineParser(this);
		try {
			parser.parseArgument(cliArgs);
		} catch (CmdLineException e) {
			System.err.println(e.getMessage());
			parser.printUsage(System.err);
		}
	}
	
	public static void main(String[] args) {
		RuleFileMerger merger = new RuleFileMerger(args);
		merger.run();
	}
}
