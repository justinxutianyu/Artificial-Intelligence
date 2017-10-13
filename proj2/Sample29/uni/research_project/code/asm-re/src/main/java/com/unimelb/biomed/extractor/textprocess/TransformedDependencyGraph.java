package com.unimelb.biomed.extractor.textprocess;


import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst.preprocessing.dp.DependencyGraph;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

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
