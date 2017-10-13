package com.unimelb.biomed.extractor;

import gov.nih.bnst.preprocessing.annotation.DocumentProducer;

import java.io.File;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.kohsuke.args4j.Argument;
import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.annotations.AnnotatedDocCollection;
import com.unimelb.biomed.extractor.annotations.AnnotatedDocument;
import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;
import com.unimelb.biomed.extractor.annotations.BnstTermAnnotation;
import com.unimelb.biomed.extractor.annotations.BnstEventAnnotation;
import com.unimelb.biomed.extractor.learning.PatternLearner;

import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.annotation.Event;

public class SharedTaskLearn extends SharedTaskRunBase {

    private static final Logger LOG
        = LoggerFactory.getLogger(SharedTaskLearn.class);

	private PatternLearner learner = new PatternLearner();

    private static final String parseDirPrefix
        = SharedTaskHelper.TRAINING_PARSE_DIR;
	private static final String rulesDir
        = SharedTaskHelper.LEARNED_RAW_RULES_DIR;

	@Argument(index=0, required=true)
    String trainDataDir;

	public SharedTaskLearn(String trainDataDir) {
		this.trainDataDir = trainDataDir;
	}

	public SharedTaskLearn(String[] cliArgs) {
		readArgs(cliArgs);
		init();
	}

	protected void learn() {
		Collection<String> parseDirs = getParseDirs();
		if (parseDirs.size() == 0)
			LOG.error("No parse files found");
		for (String parseDir : getParseDirs()) {
			LOG.debug("Adding files from {} to learner", parseDir);
			LOG.debug("Parse source is {}" , parseSource);
            LOG.debug("Relation type is {}", relationType);
            DocumentProducer docProd = getDocProducer(parseDir, trainDataDir, corpus, true);
            for (AnnotatedDocument doc : docProd.documents()) {
                if (corpus.equals("variome")) {
                    learner.addDocument(
                        doc.getId(),
                        doc.getAnnSentences(),
                        doc.getCorpus(),
                        relationType
                    );
                }
                else {
                    learner.addDocument(
                        doc.getId(),
                        doc.getAnnSentences(),
                        doc.getCorpus(),
                        ""
                    );
                }
            }
		}
		File rulesDirFile = new File(rulesDir);
		if (!rulesDirFile.exists())
			rulesDirFile.mkdir();
        learner.writeOutRules(rulesDir);
	}

	private Collection<String> getParseDirs() {
		List<String> dirs = new ArrayList<String>();
		// for backwards compatilty, accept an exact prefix match
		File baseFile = new File(parseDirPrefix);
		if (baseFile.exists()) {
			LOG.debug("Adding training dir {}", baseFile);
			dirs.add(parseDirPrefix);
		}
		for (File file : baseFile.getParentFile().listFiles()) {
			String name = file.getName();
			// accept files that have the base name of the prefix (probably
			// 'parse')
			// and the appropriate suffix as well
			if (SharedTaskHelper.PARSE_VARIANT_NAME_PTN.matcher(name).matches()) {
				LOG.debug("Adding variant training parse dir {}", file);
				dirs.add(file.getPath());
			}
		}

		return dirs;
	}

	public static void main(String[] args) {
        SharedTaskLearn stRun = new SharedTaskLearn(args);
		stRun.learn();
	}
}
