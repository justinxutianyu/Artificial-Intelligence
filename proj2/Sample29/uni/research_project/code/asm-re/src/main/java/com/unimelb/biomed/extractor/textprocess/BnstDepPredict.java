package com.unimelb.biomed.extractor.textprocess;

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
import com.unimelb.biomed.extractor.SharedTaskHelper;
import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;

public class BnstDepPredict extends BioDepPredict {

    ////////////////////////
    // Instance Variables //
    ////////////////////////

    private static final Logger LOG = LoggerFactory.getLogger(BnstDepPredict.class);

	@Option(
        name="-pretok-nes",
        usage=
            "Run preprocessing over entities from .a1 files to " +
			"make the tokenization match *before* parsing",
        required=false
    )
    private boolean pretokNes = false;


    @Option(
        name="-corpus",
        usage=
            "Indicates corpus that will be parsed, " +
            "valid options are genia, seedev and variome",
        required=true
    )
    private String corpus = "genia";

    ////////////////////////
    // Class Constructors //
    ////////////////////////

	public BnstDepPredict(String[] args) {
		super(args);
	}

    //////////////////////
    // Internal Classes //
    //////////////////////

	public static class NLProcessors {
		public AbstractSegmenter segmenter;
		public Pair<POSTagger[], Double> taggers;
		public AbstractMPAnalyzer analyzer;
		public AbstractDEPParser parser;

		public NLProcessors(
            AbstractSegmenter segmenter,
            Pair<POSTagger[], Double> taggers,
			AbstractMPAnalyzer analyzer,
            AbstractDEPParser parser
        ) {
			this.segmenter = segmenter;
			this.taggers = taggers;
			this.analyzer = analyzer;
			this.parser = parser;
		}
	}

    /**
     * Extracts a set of dependency trees from an input file,
     * and writes the result to a separate file with the
     * the same name as the input file, but with the extension
     * .parsed.
     * <p>
     * Each file is split into a collection of sentences, which
     * are in turn split into a list of tokens. The dependency
     * parse is extracted from this list of tokens.
     *
     * @param segmenter
     * @param taggers
     * @param analyzer
     * @param parser
     * @param fin
     * @param inputFile
     * @param outputFile
     *
     * @return void
     */
	@Override
	public void predict(
        AbstractSegmenter segmenter,
		Pair<POSTagger[], Double> taggers,
        AbstractMPAnalyzer analyzer,
		AbstractDEPParser parser,
        RawReader fin,
        String inputFile,
		String outputFile
    ) {
        //Initialize input and output files
		PrintStream fout =
            UTOutput.createPrintBufferedFileStream(outputFile);
        fin.open(
            UTInput.createBufferedFileReader(inputFile)
        );

        try {
			DEPTree tree;
			int i = 0;

            //Initialize NLP tools for the input file
            initializeForFile(
                segmenter, taggers, analyzer, parser, inputFile
            );

            //Extract dependency trees from each sentence
            //Note that sentences are represented as a list of tokens
            for (List<Token> tokens : segmenter.getSentences(fin.getBufferedReader())) {
                LOG.debug("Parsing sentence: {}", tokens);
                tree = EngineProcess.getDEPTree(
                    taggers, analyzer, parser, tokens
                );
				fout.println(
                    tree.toStringDEP()
					+ AbstractColumnReader.DELIM_SENTENCE
                );
			}
		}
        finally {
			fin.close();
			fout.close();
		}
	}

    /**
     * Prepares a set of NLP tools for use on a specific
     * intput (text) file.
     * <p>
     * Each tool is passed in as a parameter, and modified
     * in place to produce the resulting prepared tool.
     *
     * @param segmenter
     * @param taggers
     * @param analyzer
     * @param parser
     * @param inputFile
     *
     * @return void
     */
	public void initializeForFile(
        AbstractSegmenter segmenter,
		Pair<POSTagger[], Double> taggers,
        AbstractMPAnalyzer analyzer,
		AbstractDEPParser parser,
        String inputFile
    ) {
		initializeTaggers(taggers, inputFile);
		initializeSegmenter(segmenter, inputFile);
	}

	protected void initializeTaggers(
        Pair<POSTagger[], Double> taggers,
        String inputFile
    ) {
        String entityFile;

        if (this.corpus.equals("variome")) {
            entityFile = SharedTaskHelper.entityFileForTextFile(
                inputFile, ".ann"
            );
        }
        else {
            entityFile = SharedTaskHelper.entityFileForTextFile(
                inputFile
            );
        }

		for (POSTagger tagger : taggers.o1) {
			BnstPosTagger bpt;
			try {
				bpt = (BnstPosTagger) tagger;
				LOG.debug(
                    "Successfully cast {} to BnstPosTagger",
                    tagger
                );
			} catch (ClassCastException e) {
				LOG.warn(
                    "Tagger {} is not an instance of BnstPosTagger",
					tagger
                );
				continue;
			}
			try {
                bpt.readBioEntities(entityFile, corpus);
			} catch (BnstRuntimeException e) {
                System.out.println(e);
                System.exit(0);
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

    /////////////////
    // Main Method //
    /////////////////

	public static void main(String[] args) {
        new BnstDepPredict(args);
	}

}
