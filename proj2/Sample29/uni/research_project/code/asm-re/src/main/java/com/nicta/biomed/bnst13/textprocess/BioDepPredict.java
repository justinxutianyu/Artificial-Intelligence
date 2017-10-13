package com.nicta.biomed.bnst13.textprocess;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.PrintStream;
import java.util.List;
import java.util.zip.ZipInputStream;

import org.kohsuke.args4j.Option;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.w3c.dom.Element;

import com.googlecode.clearnlp.dependency.AbstractDEPParser;
import com.googlecode.clearnlp.dependency.DEPTree;
import com.googlecode.clearnlp.engine.EngineProcess;
import com.googlecode.clearnlp.morphology.AbstractMPAnalyzer;
import com.googlecode.clearnlp.pos.POSNode;
import com.googlecode.clearnlp.reader.AbstractColumnReader;
import com.googlecode.clearnlp.reader.POSReader;
import com.googlecode.clearnlp.run.DEPPredict;
import com.googlecode.clearnlp.segmentation.AbstractSegmenter;
import com.googlecode.clearnlp.tokenization.AbstractTokenizer;
import com.googlecode.clearnlp.tokenization.Tokenizer;
import com.googlecode.clearnlp.util.UTInput;
import com.googlecode.clearnlp.util.UTOutput;
import com.googlecode.clearnlp.util.UTXml;

public class BioDepPredict extends DEPPredict {
	private static final Logger LOG = LoggerFactory.getLogger(BioDepPredict.class);

	@Option(name = "-j", aliases = { "--jtbd-word-toks" }, usage = "Segment words using the JULIE token boundary detector")
	boolean useJtbd = false;

	public BioDepPredict() {
	}

	public BioDepPredict(String[] args) {
		super(args);
	}

	@Override
	public AbstractSegmenter getSegmenter(Element eConfig) {
		LOG.debug("Returning biomedical segmenter");
		OffsettableTokenizer tokenizer = useJtbd ? getJTBDTokenizer() : getOffsetTokenizer(eConfig);
		return new JSBDSegmenter(tokenizer);
	}

	protected OffsettableTokenizer getOffsetTokenizer(Element eConfig) {
		String dictFile = UTXml.getTrimmedTextContent(UTXml.getFirstElementByTagName(eConfig,
				TAG_DICTIONARY));
		return getBasicTokenizer(dictFile);
	}

	public static OffsettableTokenizer getBasicTokenizer(String dictFile) {
		try {
			return getBasicTokenizer(new FileInputStream(dictFile));
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		}
	}

	public static OffsettableTokenizer getBasicTokenizer(FileInputStream fileInputStream) {
		return new OffsetEnglishTokenizer(new ZipInputStream(fileInputStream));
	}

	protected OffsettableTokenizer getJTBDTokenizer() {
		return new OffsetJTBDEnglishTokenizer();
	}

	public static void main(String[] args) {
		new BioDepPredict(args);
	}

	/** Override prediction when starting with POS tags so we can read from an extended POS-tag
	 * format with character spans added
	 */
	@Override
	public void predict(AbstractMPAnalyzer analyzer, AbstractDEPParser parser, POSReader fin,
			String inputFile, String outputFile) {
		SpanPOSReader finActual = new SpanPOSReader();
		PrintStream fout = UTOutput.createPrintBufferedFileStream(outputFile);
		finActual.open(UTInput.createBufferedFileReader(inputFile));
		List<POSNode> nodes;
		System.out.print(inputFile + ": ");
		while ((nodes = finActual.next()) != null) {
			DEPTree tree = EngineProcess.getDEPTree(analyzer, parser, nodes);
			fout.println(tree.toStringDEP() + AbstractColumnReader.DELIM_SENTENCE);
		}
		System.out.println();
		finActual.close();
		fout.close();
	}

}
