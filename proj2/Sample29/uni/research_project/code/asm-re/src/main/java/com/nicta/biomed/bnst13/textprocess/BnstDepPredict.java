package com.nicta.biomed.bnst13.textprocess;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Element;

import com.googlecode.clearnlp.dependency.AbstractDEPParser;
import com.googlecode.clearnlp.dependency.DEPTree;
import com.googlecode.clearnlp.engine.EngineGetter;
import com.googlecode.clearnlp.engine.EngineProcess;
import com.googlecode.clearnlp.morphology.AbstractMPAnalyzer;
import com.googlecode.clearnlp.pos.POSTagger;
import com.googlecode.clearnlp.reader.AbstractColumnReader;
import com.googlecode.clearnlp.reader.JointReader;
import com.googlecode.clearnlp.reader.RawReader;
import com.googlecode.clearnlp.segmentation.AbstractSegmenter;
import com.googlecode.clearnlp.tokenization.AbstractTokenizer;
import com.googlecode.clearnlp.tokenization.Token;
import com.googlecode.clearnlp.util.UTInput;
import com.googlecode.clearnlp.util.UTOutput;
import com.googlecode.clearnlp.util.UTXml;
import com.googlecode.clearnlp.util.pair.Pair;
import com.nicta.biomed.bnst13.SharedTaskHelper;
import com.nicta.biomed.bnst13.annotations.BnstRuntimeException;

public class BnstDepPredict extends BioDepPredict {
	private static final Logger LOG = LoggerFactory.getLogger(BnstDepPredict.class);

	@Option(name="-pretok-nes", usage="Run preprocessing over entities from .a1 files to " +
			" make the tokenization match *before* parsing", required=false)
	private boolean pretokNes = false;
	
	public BnstDepPredict(String[] args) {
		super(args);
	}

	public static class NLProcessors {
		public AbstractSegmenter segmenter;
		public Pair<POSTagger[], Double> taggers;
		public AbstractMPAnalyzer analyzer;
		public AbstractDEPParser parser;

		public NLProcessors(AbstractSegmenter segmenter, Pair<POSTagger[], Double> taggers,
				AbstractMPAnalyzer analyzer, AbstractDEPParser parser) {
			this.segmenter = segmenter;
			this.taggers = taggers;
			this.analyzer = analyzer;
			this.parser = parser;
		}
	}
	
//	public List<DEPTree> getDepTrees(NLProcessors nlProcs,
//			RawReader fin, String inputFile,
//			String outputFile) {
//		File outf = new File(outputFile);
//		if (!outf.exists()) 
//			predict(nlProcs.segmenter, nlProcs.taggers, nlProcs.analyzer,
//					nlProcs.parser, fin, inputFile, outputFile);
//		List<DEPTree> results = new ArrayList<DEPTree>();
//		depReader.open(UTInput.createBufferedFileReader(outputFile));
//		DEPTree tree = null;
//		while ((tree = depReader.next()) != null)
//			results.add(tree);
//		return results;
//	}
//	
	@Override
	public void predict(AbstractSegmenter segmenter,
			Pair<POSTagger[], Double> taggers, AbstractMPAnalyzer analyzer,
			AbstractDEPParser parser, RawReader fin, String inputFile,
			String outputFile) {
		PrintStream fout = UTOutput.createPrintBufferedFileStream(outputFile);
		fin.open(UTInput.createBufferedFileReader(inputFile));
		try {
			DEPTree tree;
			int i = 0;

			System.out.print(inputFile + ": ");

			initializeForFile(segmenter, taggers, analyzer, parser, inputFile);
			for (List<Token> tokens : segmenter.getSentences(fin
					.getBufferedReader())) {
				tree = EngineProcess.getDEPTree(taggers, analyzer, parser,
						tokens);
				fout.println(tree.toStringDEP()
						+ AbstractColumnReader.DELIM_SENTENCE);
			}

			System.out.println();
		} finally {
			fin.close();
			fout.close();
		}
	}

	public void initializeForFile(AbstractSegmenter segmenter,
			Pair<POSTagger[], Double> taggers, AbstractMPAnalyzer analyzer,
			AbstractDEPParser parser, String inputFile) {
		initializeTaggers(taggers, inputFile);
		initializeSegmenter(segmenter, inputFile);
	}

	protected void initializeTaggers(Pair<POSTagger[], Double> taggers, String inputFile) {
		String entityFile = SharedTaskHelper.entityFileForTextFile(inputFile);
		LOG.debug("Entity file for {} is {}", inputFile, entityFile);

		for (POSTagger tagger : taggers.o1) {
			BnstPosTagger bpt;
			try {
				bpt = (BnstPosTagger) tagger;
				LOG.debug("Successfully cast {} to BnstPosTagger", tagger);
			} catch (ClassCastException e) {
				LOG.warn("Tagger {} is not an instance of BnstPosTagger",
						tagger);
				continue;
			}
			try {
				bpt.readBioEntities(entityFile);
			} catch (IOException e) {
				throw new BnstRuntimeException(e);
			}
		}
	}

	protected Pair<POSTagger[], Double> getPOSTaggers(Element eConfig) {
		LOG.debug("Getting BNST POS taggers for BnstDepPredict");
		try {
			String modelFile = UTXml.getTrimmedTextContent(UTXml
					.getFirstElementByTagName(eConfig, TAG_POS_MODEL));
			return BnstEngineGetter.getPOSTaggers(modelFile);
		} catch (Exception e) {
			e.printStackTrace();
		}

		return null;
	}
	
	@Override
	protected OffsettableTokenizer getOffsetTokenizer(Element eConfig) {
		if (pretokNes)
			return getPretokNETokenizer(eConfig);
		else
			return super.getOffsetTokenizer(eConfig);
	}

	private OffsettableTokenizer getPretokNETokenizer(Element eConfig) {
		String dictFile = UTXml.getTrimmedTextContent(UTXml.getFirstElementByTagName(eConfig,
				TAG_DICTIONARY));
		return BnstEngineGetter.getTokenizerForPretokNEs(dictFile);
	}

	
	protected void initializeSegmenter(AbstractSegmenter segmenter, String inputFile) {
		if (!pretokNes)
			return;
		JSBDSegmenter jSeg;
		try {
			jSeg = (JSBDSegmenter) segmenter;
			LOG.debug("Successfully cast {} to JSBDSegmenter", segmenter);
		} catch (ClassCastException e) {
			throw new RuntimeException("Segmenter " + segmenter
					+ " must be a JSBDSegmenter instance", e);
		}
		BnstEnglishTokenizer bnstTok;
		try {
			bnstTok = (BnstEnglishTokenizer) jSeg.getOffsetTokenizer();
			if (LOG.isDebugEnabled())
				LOG.debug("Successfully cast {} to BnstEnglishTokenizer", jSeg.getOffsetTokenizer());
		} catch (ClassCastException e) {
			throw new RuntimeException("Tokenizer " + jSeg.getOffsetTokenizer()
					+ " must be a BnstEnglishTokenizer instance", e);
		}

		String entityFile = SharedTaskHelper.entityFileForTextFile(inputFile);
		try {
			bnstTok.readBioEntities(entityFile);
		} catch (IOException e) {
			throw new BnstRuntimeException(e);
		}

	}

	public static void main(String[] args) {
		new BnstDepPredict(args);
	}

}
