package com.nicta.biomed.bnst13;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.SortedSet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.util.Span;

public class SpanBoundsIndexer<V> {
	private static final Logger LOG = LoggerFactory.getLogger(SpanBoundsIndexer.class);
	
	RangeIndexer<Integer, V> beginIndexer = new RangeIndexer<Integer, V>();
	RangeIndexer<Integer, V> endIndexer = new RangeIndexer<Integer, V>();
	
	public void index(Span span, V targetVal) {
		LOG.trace("{} in begin indexer; {} in end indexer", span.begin, span.end);
		beginIndexer.put(span.begin, targetVal);
		endIndexer.put(span.end, targetVal);
	}
	
	public List<V> startingWithin(Span querySpan) {
		return beginIndexer.inRange(querySpan.begin, querySpan.end);
	}

	public List<V> endingWithin(Span querySpan) {
		return endIndexer.inRange(querySpan.begin + 1, querySpan.end + 1); // +1 since half-open
	}
	
	public List<V> overlaps(Span querySpan) {
		List<V> allOverlaps = new ArrayList<V>();
		if (LOG.isTraceEnabled()) 
			LOG.trace("For span {}, values {} start within the range, and {} end within it",
					querySpan, startingWithin(querySpan), endingWithin(querySpan));
		allOverlaps.addAll(startingWithin(querySpan));
		allOverlaps.addAll(endingWithin(querySpan));
		
		Set<V> knownVals = new HashSet<V>();
		List<V> overlaps = new ArrayList<V>(); // no duplicates
		for (V val : allOverlaps) {
			if (knownVals.contains(val))
				continue;
			knownVals.add(val);
			overlaps.add(val);
		}
		return overlaps;
	}

}

