package gov.nih.bnst.patternlearning;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.Test;

import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

/**
 * <br>Unit test cases to test the implementation of the PatternLearning module</br>
 * <br></br>
 * @author Tested by Haibin Liu
 * </br>
 *
 */

public class PatternLearningTest {

	//private PatternLearning pl = new PatternLearning("M");
	
	/**
	 * Checking if two identical graphs are isomporphic, independent of token-Id and independent of edge ordering
	 */
	@Test
	public void isComputePathUnionCorrect(){
		String g1 = "nn(type-2, Th1/Th2-1); nn(type-2, ABC-3)";
		String g2 = "nn(type-2, Th1/Th2-1); nn(type-2, DEF-4)";
		String g3 = "nn(type-2, Th1/Th2-1); nn(type-2, GHI-5)";
		
		DirectedGraph<Vertex,Edge> graph1 = createGraph(g1);
		DirectedGraph<Vertex,Edge> graph2 = createGraph(g2);
		DirectedGraph<Vertex,Edge> graph3 = createGraph(g3);
		
		List<List<DirectedGraph<Vertex, Edge>>> paths = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
		List<DirectedGraph<Vertex, Edge>> temp1 = new ArrayList<DirectedGraph<Vertex, Edge>>(); temp1.add(graph1);
		List<DirectedGraph<Vertex, Edge>> temp2 = new ArrayList<DirectedGraph<Vertex, Edge>>(); temp2.add(graph2); temp2.add(graph3);
		paths.add(temp1); paths.add(temp2);
		List<DirectedGraph<Vertex, Edge>> results = new ArrayList<DirectedGraph<Vertex, Edge>>();
		results = PatternLearning.computePathUnion(paths);
		assertEquals(2, results.size());
		DirectedGraph<Vertex, Edge> result1 = results.get(0); 
		assertEquals(3, result1.getEdgeCount()); System.out.println(result1.getEdges());
		assertEquals(4, result1.getVertexCount()); System.out.println(result1.getVertices());
		DirectedGraph<Vertex, Edge> result2 = results.get(1); 
		assertEquals(3, result2.getEdgeCount()); System.out.println(result2.getEdges());
		assertEquals(4, result2.getVertexCount()); System.out.println(result2.getVertices());
	}
	
	@Test
	public void isPatternLearningCorrect(){
	    PatternLearning pl = new PatternLearning();	
	}
	
	/**
	 * Create graphs from dependency representation
	 * @param r : input dependency representation separated by ";"
	 * @return created dependency graph
	 */
	public static DirectedGraph createGraph(String r) {
		DirectedSparseGraph<Vertex,Edge> graph = new DirectedSparseGraph<Vertex,Edge>();
		Map<String, Vertex> tokenToNode = new HashMap<String, Vertex>();
		/** dr: a single dependency representation */
		for ( String dr : r.split("\\s*;\\s*") ) {
			if ( ! dr.matches("^\\S+\\(\\S+\\s*,\\s*\\S+\\)\\s*$") )
		    	throw new RuntimeException("The dependency representation: "
						+ dr + " is not valid. Please check.");	
		    Matcher md = Pattern.compile("^(\\S+)\\((\\S+)\\s*,\\s*(\\S+)\\)\\s*$").matcher(dr);
		    md.find();
		    String label = md.group(1);  
		    String g = md.group(2); 
		    String d = md.group(3);

		    Vertex gov;
		    if(!tokenToNode.containsKey(g)) {
		        gov = new Vertex(g);
		        graph.addVertex(gov);
		        tokenToNode.put(g, gov);
		    }
		    else { gov = tokenToNode.get(g); }
		    
		    Vertex dep;
		    if(!tokenToNode.containsKey(d)) {
		        dep = new Vertex(d);
		        graph.addVertex(dep);
		        tokenToNode.put(d, dep);
		    }   
		    else { dep = tokenToNode.get(d); }
		    
		    Edge govToDep = new Edge(gov, label, dep);		    
		    graph.addEdge(govToDep, gov, dep);
		}	
		
		return graph;
    }
}
