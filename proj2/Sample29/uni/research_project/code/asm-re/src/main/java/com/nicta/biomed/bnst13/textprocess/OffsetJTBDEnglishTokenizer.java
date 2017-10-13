package com.nicta.biomed.bnst13.textprocess;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import com.googlecode.clearnlp.tokenization.Token;

import de.julielab.jtbd.JTBDException;
import de.julielab.jtbd.Tokenizer;
import de.julielab.jtbd.Unit;

public class OffsetJTBDEnglishTokenizer implements OffsettableTokenizer {
	public Tokenizer jtbdTok = new Tokenizer();
	
	public OffsetJTBDEnglishTokenizer() {
		try {
			jtbdTok.readDefaultModel();
		} catch (IOException e) {
			throw new IllegalArgumentException(e);
		} catch (ClassNotFoundException e) {
			throw new IllegalArgumentException(e);
		}
	}
	
	@Override
	public List<Token> getTokens(BufferedReader fin) {
		List<Token> tokens = new ArrayList<Token>();
		String line;
		try {
			while ((line = fin.readLine()) != null)
				tokens.addAll(getTokens(line.trim()));
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		return tokens;
	}

	@Override
	public List<Token> getTokens(String str) {
		List<Unit> tokUnits;
		try {
			tokUnits = jtbdTok.predict(str);
		} catch (JTBDException e) {
			throw new RuntimeException(e);
		}
		List<Token> toks = new ArrayList<Token>();
		for (Unit tu : tokUnits) {
			toks.add(new Token(tu.rep, tu.begin, tu.end));
		}
		return toks;
	}

	@Override
	public List<Token> getTokensWithOffset(String str, int offset) {
		List<Token> tokens = getTokens(str);
		for (Token tok : tokens) {
			tok.getSpan().addOffset(offset);
		}
		return tokens;
	}

}
