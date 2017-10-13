package com.unimelb.biomed.extractor.textprocess;

import java.util.List;
import java.util.zip.ZipInputStream;

import com.googlecode.clearnlp.tokenization.EnglishTokenizer;
import com.googlecode.clearnlp.tokenization.Token;

public class OffsetEnglishTokenizer extends EnglishTokenizer implements OffsettableTokenizer {

	public OffsetEnglishTokenizer(ZipInputStream zin) {
		super(zin);
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
