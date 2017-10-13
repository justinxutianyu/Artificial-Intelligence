package com.unimelb.biomed.extractor.textprocess;

import java.util.Comparator;

import com.googlecode.clearnlp.util.Span;

class SpanComparator implements Comparator<Span> {

	public int compare(Span o1, Span o2) {
		if (o1.begin < o2.begin)
			return -1;
		else if (o1.begin > o2.begin)
			return 1;
		else if (o1.end < o2.end) // begins are equal
			return -1;
		else if (o1.end > o2.end)
			return 1;
		else
			// equal
			return 0;
	}

}