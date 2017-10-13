package com.nicta.biomed.bnst13.textprocess;


import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst13.preprocessing.dp.DependencyGraph;
import gov.nih.bnst13.preprocessing.dp.Edge;
import gov.nih.bnst13.preprocessing.dp.Vertex;

public class TransformedDependencyGraph implements DependencyGraph {

	private DependencyGraph orig;
	private DirectedGraph<Vertex, Edge> transformed;
	
	public TransformedDependencyGraph(DependencyGraph orig, GraphTransformer transformer) {
		transformed = transformer.transform(orig.getGraph());
	}
	
	@Override
	public DirectedGraph<Vertex, Edge> getGraph() {
		return transformed;
	}

	@Override
	public Vertex getNodeFromToken(String token) {
		return orig.getNodeFromToken(token);
	}
	
	
}
