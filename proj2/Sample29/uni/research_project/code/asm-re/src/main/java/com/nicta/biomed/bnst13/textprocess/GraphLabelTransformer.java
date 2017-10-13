package com.nicta.biomed.bnst13.textprocess;

import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst13.preprocessing.dp.Edge;
import gov.nih.bnst13.preprocessing.dp.Vertex;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class GraphLabelTransformer implements GraphTransformer {
	private Map<String, String> labelReplacements;
	
	public GraphLabelTransformer(Map<String, String> labelReplacements) {
		this.labelReplacements = labelReplacements;
	}
	
	public DirectedGraph<Vertex, Edge> transform(DirectedGraph<Vertex, Edge> orig) {
		List<Edge> removeable = new ArrayList<Edge>();
		List<Edge> insertable = new ArrayList<Edge>();
		
		for (Edge edge : orig.getEdges()) {
			String newLabel = labelReplacements.get(edge.getLabel());
			if (newLabel != null) {
				removeable.add(edge);
				insertable.add(new Edge(edge.getGovernor(), newLabel, edge.getDependent()));
			}
		}
		for (Edge edge : removeable)
			orig.removeEdge(edge);
		for (Edge newEdge : insertable) 
			orig.addEdge(newEdge, newEdge.getGovernor(), newEdge.getDependent());
		return orig;
	}
}
