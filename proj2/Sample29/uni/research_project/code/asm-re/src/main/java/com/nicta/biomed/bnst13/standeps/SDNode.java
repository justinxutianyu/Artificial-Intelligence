package com.nicta.biomed.bnst13.standeps;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SDNode {
	static final Pattern NODE_PATTERN = Pattern.compile("(\\S+)-(\\d+)/(\\S+)");
	/** the number of groups in `NODE_PATTERN */ 
	static final int NODE_PATTERN_NUM_GROUPS = 3;
	
	public SDNode(int id, String form, String pos) {
		this.id = id;
		this.form = form;
		this.pos = pos;
	}
	
	public SDNode(String nodeTextRep) {
		Matcher matcher = NODE_PATTERN.matcher(nodeTextRep);
		if (!matcher.matches())
			throw new IllegalArgumentException("Invalid node representation '" + nodeTextRep + "'");
		form = matcher.group(1);
		id = Integer.parseInt(matcher.group(2));
		pos = matcher.group(3);
	}

	public int getId() {
		return id;
	}

	public String getForm() {
		return form;
	}

	public String getPos() {
		return pos;
	}

	private int id;
	private String form;
	private String pos;

	public String toString() {
		return form + "-" + id + "/" + pos;
	}
}
