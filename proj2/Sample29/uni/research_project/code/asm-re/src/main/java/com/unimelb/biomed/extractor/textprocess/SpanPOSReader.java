package com.unimelb.biomed.extractor.textprocess;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.googlecode.clearnlp.pos.POSNode;
import com.googlecode.clearnlp.reader.AbstractColumnReader;
import com.googlecode.clearnlp.reader.AbstractReader;
import com.googlecode.clearnlp.reader.POSReader;
import com.googlecode.clearnlp.util.Span;

public class SpanPOSReader extends AbstractColumnReader<List<POSNode>> {
	private static final int I_FORM = 0;
	private static final int I_POS = 1;
	private static final int I_START_SPAN = 2;
	private static final int I_END_SPAN = 3;

	@Override
	public List<POSNode> next() {
		try {
			List<POSNode> nodes = null;
			List<String[]> lines = readLines();
			if (lines == null)
				return null;
			nodes = new ArrayList<POSNode>(lines.size());
			for (String[] comps : lines) {
				int begin = Integer.parseInt(comps[I_START_SPAN]);
				int end = Integer.parseInt(comps[I_END_SPAN]);
				POSNode pn = new POSNode();
				pn.init(comps[I_FORM], comps[I_POS], AbstractReader.DUMMY_TAG, new Span(begin, end));
				nodes.add(pn);
			}
			return nodes;
		} catch (Exception e) {
			throw new RuntimeException(e);
		}
	}

	@Override
	public String getType() {
		return TYPE_POS;
	}

}
