package com.unimelb.biomed.extractor.textprocess;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import com.googlecode.clearnlp.segmentation.AbstractSegmenter;
import com.googlecode.clearnlp.tokenization.AbstractTokenizer;
import com.googlecode.clearnlp.tokenization.Token;
import com.googlecode.clearnlp.tokenization.Tokenizer;

import de.julielab.jsbd.JSBDException;
import de.julielab.jsbd.SentenceSplitter;
import de.julielab.jsbd.Unit;
import edu.umass.cs.mallet.base.pipe.Pipe;
import edu.umass.cs.mallet.base.types.Instance;
import edu.umass.cs.mallet.base.types.LabelSequence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JSBDSegmenter extends AbstractSegmenter {
	private static final Logger LOG = LoggerFactory.getLogger(JSBDSegmenter.class);
	protected final SentenceSplitter splitter = new SentenceSplitter();
	
	private OffsettableTokenizer offset_tokenizer;

	public JSBDSegmenter(OffsettableTokenizer tokenizer) {
		super(tokenizer);
		offset_tokenizer = tokenizer;
		try {
			splitter.readDefaultModel();
		} catch (IOException e) {
			throw new IllegalArgumentException(e);
		} catch (ClassNotFoundException e) {
			throw new IllegalArgumentException(e);
		}
	}

	public Tokenizer getOffsetTokenizer() {
		return offset_tokenizer;
	}
	
	
	@Override
	public List<List<Token>> getSentences(BufferedReader fin) {
		// make prediction data
		Pipe myPipe = splitter.getModel().getInputPipe();
		String line = null;
		ArrayList<String> lines = new ArrayList<String>();
		lines.add(""); // dummy first element; only first is used
		List<List<Token>> sentences = new ArrayList<List<Token>>();
		int charsSeenInFile = 0;
		try {
			while ((line = fin.readLine()) != null) {
				LOG.trace("Splitting line '{}'", line);
				int prevEndInLine = 0;
				lines.set(0, line); //recycle
				Instance inst = splitter.makePredictionData(lines, myPipe);

				ArrayList<Unit> units = null;
				try {
					units = splitter.predict(inst, false);
				} catch (JSBDException e) {
					throw new RuntimeException(e);
				}

				ArrayList<String> labels = new ArrayList<String>();
				LabelSequence ls = (LabelSequence) inst.getTarget();
				for (int j = 0; j < ls.size(); j++)
					labels.add((String) ls.get(j));

				for (Unit unit : units) {
					if (unit.label.equals("EOS")) {
						String sentence = line.substring(prevEndInLine, unit.end);
						LOG.trace("At {}:{}, found sentence '{}'", prevEndInLine, unit.end, sentence);
						List<Token> tokens = offset_tokenizer.getTokensWithOffset(sentence, charsSeenInFile + prevEndInLine);
						LOG.trace("Sentence tokens are: {}", tokens);
						prevEndInLine = unit.end;
						sentences.add(tokens);
					}
				}
				String tail = line.substring(prevEndInLine);
				if (tail.length() > 0 && !tail.matches("\\s+")) { // not only whitespace
					LOG.trace("At tail location {}:{}, found sentence '{}'", prevEndInLine, line.length(), tail);
					List<Token> tokens = offset_tokenizer.getTokensWithOffset(tail, charsSeenInFile + prevEndInLine);
					LOG.trace("Sentence tokens are: {}", tokens);
					sentences.add(tokens);
				}
				charsSeenInFile += line.length() + 1; // XXX: assumes only one newline character
				LOG.trace("Have now seen {} chars in file", charsSeenInFile);
			}
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		return sentences;

	}

}
