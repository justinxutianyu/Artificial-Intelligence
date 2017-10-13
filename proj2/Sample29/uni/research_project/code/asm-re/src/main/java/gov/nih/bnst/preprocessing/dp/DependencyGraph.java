package gov.nih.bnst.preprocessing.dp;

import java.util.Arrays;
import java.util.Collection;
import java.util.Map;
import java.util.Set;

import edu.ucdenver.ccp.nlp.biolemmatizer.BioLemmatizer;
import edu.uci.ics.jung.graph.DirectedGraph;

public interface DependencyGraph {


	/**
	 * retrieve the dependency graph defined in JUNG package
	 * @return graph
	 */
	public DirectedGraph<Vertex,Edge> getGraph();

	/**
	 * retrieve the node of the graph using its token
	 * @return node of the graph
	 */
	public Vertex getNodeFromToken(String token);
}