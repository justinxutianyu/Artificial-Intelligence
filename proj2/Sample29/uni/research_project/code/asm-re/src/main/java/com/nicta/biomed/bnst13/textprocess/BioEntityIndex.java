package com.nicta.biomed.bnst13.textprocess;

import java.io.IOException;
import java.util.List;
import java.util.SortedMap;
import java.util.SortedSet;
import java.util.TreeMap;
import java.util.TreeSet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.util.Span;
import com.nicta.biomed.bnst13.SpanBoundsIndexer;
import com.nicta.biomed.bnst13.annotations.BnstTermAnnotation;

public class BioEntityIndex {
	private static final Logger LOG = LoggerFactory.getLogger(BioEntityIndex.class);
	
	private SortedMap<Span, Integer> bioEntities = new TreeMap<Span, Integer>(new SpanComparator());
	private SpanBoundsIndexer<Span> beSpanIndexer;

	public SortedMap<Span, Integer> entities() {
		return bioEntities;
	}

	public SpanBoundsIndexer<Span> spanIndexer() {
		return beSpanIndexer;
	}

	public SortedSet<Integer> getBoundsWithinSpan(Span tokSpan) {
		List<Span> overlapping = beSpanIndexer.overlaps(tokSpan);
		SortedSet<Integer> allBounds = new TreeSet<Integer>();
		allBounds.add(tokSpan.begin);
		for (Span overlap : overlapping) {
			for (int bound : new int[] { overlap.begin, overlap.end }) {
				if (bound > tokSpan.begin && bound < tokSpan.end)
					allBounds.add(bound);
			}
		}
		allBounds.add(tokSpan.end);
		return allBounds;
	}

	public void read(String fileName) throws IOException {
		bioEntities.clear();
		for (BnstTermAnnotation termAnn : BnstTermAnnotation.readFile(fileName)) {
			bioEntities.put(termAnn.getSpan(), termAnn.getIntegerId());
		}
		beSpanIndexer = new SpanBoundsIndexer<Span>();
		for (Span span : bioEntities.keySet())
			beSpanIndexer.index(span, span);

	}
}