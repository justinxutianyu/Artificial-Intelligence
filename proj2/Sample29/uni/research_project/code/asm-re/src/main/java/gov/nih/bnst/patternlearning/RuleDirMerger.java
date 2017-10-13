package gov.nih.bnst.patternlearning;

import java.io.File;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RuleDirMerger {
	private static final Logger LOG = LoggerFactory.getLogger(RuleDirMerger.class);
	
	/** merges two rule files, removing newly-introduced isomorphism */
	
	@Argument
	private List<String> ruleDirs = new ArrayList<String>();
	
	/** path to the new rule */
	@Option(name="-o", aliases="--output-dir", required=true)
	private String outputDir = "merged-rules";

	public RuleDirMerger(String[] args) {
		readArgs(args);
	}
	
	protected void run() {
		Set<String> categories = new HashSet<String>();
		for (String ruleSubDir : ruleDirs) {
			for (String categ : new File(ruleSubDir).list())
				categories.add(categ);
		}
		LOG.warn("Categories are: {}", categories);
		for (String categ : categories) {
			List<String> ruleFiles = new ArrayList<String>();
			for (String ruleSubDir : ruleDirs) {
				File possFile = new File(ruleSubDir, categ);
				if (possFile.exists())
					ruleFiles.add(possFile.getAbsolutePath());
			}
			LOG.warn("Rule files for {} are: {}", categ, ruleFiles);
			RuleFileMerger fileMerger = new RuleFileMerger(ruleFiles, outputDir);
			fileMerger.run();
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
		RuleDirMerger merger = new RuleDirMerger(args);
		merger.run();
	}
}
