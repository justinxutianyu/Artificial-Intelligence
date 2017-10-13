package com.unimelb.biomed.extractor.textprocess;

import java.util.List;

import com.googlecode.clearnlp.tokenization.Token;
import com.googlecode.clearnlp.tokenization.Tokenizer;

public interface OffsettableTokenizer extends Tokenizer {

	/** Like getTokens(), but all spans will be offset by `offset` characters */
	public List<Token> getTokensWithOffset(String str, int offset);

	
}
