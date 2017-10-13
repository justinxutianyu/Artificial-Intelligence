package com.unimelb.biomed.extractor.textprocess;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.zip.ZipInputStream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.tokenization.EnglishTokenizer;
import com.googlecode.clearnlp.tokenization.FlaggedToken;
import com.googlecode.clearnlp.tokenization.Token;
import com.googlecode.clearnlp.util.Span;
import com.unimelb.biomed.extractor.SpanBoundsIndexer;
import com.unimelb.biomed.extractor.annotations.BnstTermAnnotation;

/**
 * Variant of EnglishTokenizer which handles named entities more sensibly. The
 * complete NE is inserted into a single token, while any leading or trailing
 * text is converted into its own token
 * 
 * @author amack
 * 
 */
public class BnstEnglishTokenizer extends EnglishTokenizer implements OffsettableTokenizer {
	private static final Logger LOG = LoggerFactory.getLogger(BnstEnglishTokenizer.class);

	private BioEntityIndex bioEntIndex = new BioEntityIndex();

	public BnstEnglishTokenizer(ZipInputStream zin) {
		super(zin);
	}

	public void readBioEntities(String fileName) throws IOException {
		bioEntIndex.read(fileName);
	}

	public List<FlaggedToken> getTokenList(String str, int offset) {
		List<FlaggedToken> toks = super.getTokenList(str);
		for (FlaggedToken flTok : toks)
			flTok.tok.getSpan().addOffset(offset);
		toks = splitAtEntityBoundaries(toks);
		toks = mergeMultiTokenNEs(toks);
		return toks;
	}

	private List<FlaggedToken> mergeMultiTokenNEs(List<FlaggedToken> toks) {
		SpanBoundsIndexer<Integer> spanIndexer = new SpanBoundsIndexer<Integer>();
		int sentenceBeginIdx = toks.get(0).tok.getSpan().begin;
		int sentenceEndIdx = toks.get(toks.size() - 1).tok.getSpan().end;
		for (int i = 0; i < toks.size(); i++) {
			Token tok = toks.get(i).tok;
			LOG.trace("Indexing token '{}' ({}) at span {}", tok, i, tok.getSpan());
			spanIndexer.index(tok.getSpan(), i);
		}
		List<ReplaceableRange> replaceable = new ArrayList<ReplaceableRange>();
		for (Map.Entry<Span, Integer> spanIdEntry : bioEntIndex.entities().entrySet()) {
			Span beSpan = spanIdEntry.getKey(); // bioentity span
			if (sentenceEndIdx < beSpan.begin || sentenceBeginIdx > beSpan.end) {
				LOG.trace("Sentence at {}:{} has no overlaps with entity at {}; skipping",
						sentenceBeginIdx, sentenceEndIdx, beSpan);
				continue;
			}
			List<Integer> overlaps = spanIndexer.overlaps(beSpan);
			
			LOG.trace("Matched bio-entity span {} to POS nodes {}", beSpan, overlaps);
			if (overlaps.size() <= 1) {
				if (overlaps.isEmpty()) {
					LOG.warn("No tokens found within span {}", beSpan);
				continue; // 1 -> exact span match, as tokens are split to match NEs
			}
			Collections.sort(overlaps);
			ReplaceableRange repRange = new ReplaceableRange();
			int first = overlaps.get(0);
			int last = overlaps.get(overlaps.size() - 1);
			repRange.firstIndex = first;
			repRange.lastIndex = last;
			
			StringBuffer tokText = new StringBuffer();
			for (int idx : overlaps) 
				tokText.append(toks.get(idx).tok.getText()); // ignoring spaces (if any)
			Token repTok = new Token(tokText.toString(), beSpan);
			repRange.replacements.add(new FlaggedToken(repTok, false));
			
			replaceable.add(repRange);
			
			}
			LOG.trace("Replaceables list is now: {}", replaceable );
		}
		if (!replaceable.isEmpty()) {
			// length changed due to multi-token NE
			LOG.trace("There are {} replacements to make after NE preprocessing", replaceable.size());
			List<FlaggedToken> origToks = toks;
			toks = new ArrayList<FlaggedToken>();
			Iterator<ReplaceableRange> replIter = replaceable.iterator();
			int i = 0;
			while (replIter.hasNext()) {
				ReplaceableRange nextRep = replIter.next();
				LOG.trace("Inserting original tokens from indices {}:{}", i, nextRep.firstIndex);
				LOG.trace("Inserting replacement {}", nextRep);
				toks.addAll(origToks.subList(i, nextRep.firstIndex)); // original
				toks.addAll(nextRep.replacements);
				i = nextRep.lastIndex + 1;
			}
			// everything after final rep range:
			LOG.trace("Inserting (sentence-final) original toks from {} to {}", i, origToks.size());
			toks.addAll(origToks.subList(i, origToks.size())); 
		}
		return toks;
	}

	private List<FlaggedToken> splitAtEntityBoundaries(List<FlaggedToken> toks) {
		List<FlaggedToken> newToks = new ArrayList<FlaggedToken>();
		for (FlaggedToken flTok : toks) {
			Token tok = flTok.tok;
			Span tokSpan = tok.getSpan();

			SortedSet<Integer> allBounds = bioEntIndex.getBoundsWithinSpan(tokSpan);

			if (allBounds.size() == 2) { // start and end only
				LOG.trace("No bioentities overlap with '{}'@{}", tok, tok.getSpan());
				newToks.add(flTok);
				continue;
			}
			LOG.trace("Entity boundaries from overlaps with '{}'@{} are: {}", 
					tok, tok.getSpan(), allBounds);
			for (Integer end : allBounds.tailSet(allBounds.first() + 1)) {
				int begin = allBounds.headSet(end).last(); // the one before
				int relBegin = begin - tokSpan.begin;
				int relEnd = end - tokSpan.begin;
				Token splitTok = new Token(tok.getText().substring(relBegin, relEnd), begin, end);
				LOG.trace("Adding new token '{}'@{}", splitTok, splitTok.getSpan());
				newToks.add(new FlaggedToken(splitTok, flTok.flag));
			}
		}
		if (LOG.isDebugEnabled()) {
			List<Token> replToks = new ArrayList<Token>();
			for (FlaggedToken flTok: newToks)
				replToks.add(flTok.tok);
			LOG.debug("After splitting, tokens are: {}", replToks);
		}
		return newToks;
	}

	@Override
	public List<Token> getTokensWithOffset(String str, int offset) {
		List<FlaggedToken> lTokens = getTokenList(str, offset);
		List<Token> tokens = new ArrayList<Token>(lTokens.size());
		
		for (FlaggedToken fTok : lTokens)
			tokens.add(fTok.tok);
		
		return tokens;
	}
	
	@Override
	public List<Token> getTokens(String str)
	{
		return getTokensWithOffset(str, 0);
	}
	
	@Override
	public List<FlaggedToken> getTokenList(String str) {
		return getTokenList(str, 0);
	}

}

class ReplaceableRange {
	/**
	 * the token (not char) starting index from which the existing tokens should
	 * be removed
	 */
	int firstIndex;
	/** The last index to be removed */
	int lastIndex;

	/** The new tokens to be inserted */
	List<FlaggedToken> replacements = new ArrayList<FlaggedToken>();
	
	public String toString() {
		List<Token> replToks = new ArrayList<Token>();
		for (FlaggedToken flTok: replacements)
			replToks.add(flTok.tok);
		return firstIndex + ":" + lastIndex + " --> " + replToks;		
	}
}
