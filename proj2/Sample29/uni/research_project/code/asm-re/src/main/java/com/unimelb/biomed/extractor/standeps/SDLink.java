package com.unimelb.biomed.extractor.standeps;


public class SDLink {
	private String name;
	private int from;
	private int to;
	private SDLikeDepGraph tree;
	
	public SDLink(String name, int from, int to, SDLikeDepGraph tree) {
		this.name = name;
		this.from = from;
		this.to = to;
		this.tree = tree;
	}
	
	public String toString() {
		return name + "(" + tree.getNode(from) + ", " + tree.getNode(to) + ")";
	}

	public String getName() {
		return name;
	}

	public int getFrom() {
		return from;
	}

	public int getTo() {
		return to;
	}
	
}
