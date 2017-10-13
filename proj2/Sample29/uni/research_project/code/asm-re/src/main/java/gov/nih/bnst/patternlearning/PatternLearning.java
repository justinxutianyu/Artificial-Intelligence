package gov.nih.bnst.patternlearning;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;


import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import edu.uci.ics.jung.algorithms.shortestpath.DijkstraShortestPath;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import gov.nih.bnst.preprocessing.annotation.Event;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.combine.training.CombineInfo;
import gov.nih.bnst.preprocessing.combine.training.ReadSingleSentenceOutput;
import edu.ucdenver.ccp.esm.ESM;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;


/**
 * pattern learning module of the event extraction system
 * @author liuh11
 *
 */
public class PatternLearning {
	/** store all extracted event rules */
	Map<String, List<EventRule>> allEventRules = new HashMap<String, List<EventRule>>();
	/** store extracted event rules without isomorphic rules */
	Map<String, List<EventRule>> eventRulesWithoutIsomorphism = new HashMap<String, List<EventRule>>();
	
	private class CustomESM extends ESM<Vertex, Edge> {
		public CustomESM(DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph) {
			super(subgraph, graph);
		}
	}
	
	/**
	 * Constructor to initialize pattern learning module
	 */
	public PatternLearning() {
		/** graph type to be retrieved: M stands for McClosky; S stands for Stanford */
		for (String graphType : new String[] { "M", "S"}) {
	    //preprocessing 
			CombineInfo annotation = new CombineInfo(graphType);
			Map<String, List<ReadSingleSentenceOutput>> documents = annotation.getAnnotatedDocuments();
			//event rule generation
			generateGraphPatternsForEachDocument(documents);
		}
	    //remove rules that have isomorphic dependency graph with other rules
	    removeIsomorphicPaths();
	    //write rules to files
	    writeEventRulesToFiles();
	}
	
	private void generateGraphPatternsForEachDocument(Map<String, List<ReadSingleSentenceOutput>> documents) {
		int fileCount = 0;
		for(String pmid : documents.keySet()) {
			System.out.println("extracting from ...... " + pmid + " the " + ++fileCount + " file.");
			for(AnnotatedSentence sentence : documents.get(pmid)) {
				//System.out.println("sentence " + sentence.getSentenceID() + " " + sentence.getStartIndex() + " " + sentence.getEndIndex());
				if(sentence.getEvents() == null) { continue; }
				DirectedGraph<Vertex, Edge> graph = sentence.getDependencyGraph().getGraph();
				List<EventRule> eventRulesOfSentence = new ArrayList<EventRule>();
				for(String e : sentence.getEvents().keySet()) {
					Event event = sentence.getEvents().get(e); 
					//System.out.println(sentence.getEvents().get(e).toA2String());
					//Binding events
					if(event.getEventCategory().equals("Binding")) {
						List<List<DirectedGraph<Vertex, Edge>>> extractedPathsCombined = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
						for(int i=0; i<event.getEventThemes().size(); i++) {
							Vertex theme = sentence.getProteins().get(event.getEventThemes().get(i)).getGraphNode();
							Set<Vertex> triggers = sentence.getTriggers().get(event.getEventTrigger()).getTriggerNodes();
						    List<List<DirectedGraph<Vertex, Edge>>> extractedPaths = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
						    for(Vertex trigger : triggers) {
	                        	extractedPaths.add(findShortestPaths(graph, trigger, theme));
						    	//extractedPaths.add(findAllPaths(graph, trigger, theme));
						    }
						    List<DirectedGraph<Vertex, Edge>> results = computePathUnion(extractedPaths);
						    extractedPathsCombined.add(results);
						}
						List<DirectedGraph<Vertex, Edge>> resultsFinal = computePathUnion(extractedPathsCombined);
					    for(DirectedGraph<Vertex, Edge> path : resultsFinal) {
	                		EventRule pattern = new EventRule(path, event, sentence, pmid);
	                		eventRulesOfSentence.add(pattern);	
					    }
					}
					//simple events
					else if(!event.getEventCategory().endsWith("egulation")) {
						Vertex theme = sentence.getProteins().get(event.getEventThemes().get(0)).getGraphNode();
					    Set<Vertex> triggers = sentence.getTriggers().get(event.getEventTrigger()).getTriggerNodes();
					    List<List<DirectedGraph<Vertex, Edge>>> extractedPaths = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
					    for(Vertex trigger : triggers) {
                        	extractedPaths.add(findShortestPaths(graph, trigger, theme));
					    	//extractedPaths.add(findAllPaths(graph, trigger, theme));
					    }
					    List<DirectedGraph<Vertex, Edge>> results = computePathUnion(extractedPaths);
					    for(DirectedGraph<Vertex, Edge> path : results) {
	                		EventRule pattern = new EventRule(path, event, sentence, pmid);
	                		eventRulesOfSentence.add(pattern);	
					    }
					}
					//complex events
					else {
						List<List<DirectedGraph<Vertex, Edge>>> extractedPathsCombined = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
						//theme argument
						Vertex theme;
						//no subevent
						if(event.getEventThemes().get(0).charAt(0) == 'T') {
					    	theme = sentence.getProteins().get(event.getEventThemes().get(0)).getGraphNode();
					    }
						//with subevent
						else {
							String trigger = sentence.getEvents().get(event.getEventThemes().get(0)).getEventTrigger();
						    theme = sentence.getTriggers().get(trigger).getTriggerCenterNode();    	
						}
						Set<Vertex> triggers = sentence.getTriggers().get(event.getEventTrigger()).getTriggerNodes();
					    List<List<DirectedGraph<Vertex, Edge>>> extractedPaths = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
					    for(Vertex trigger : triggers) {
                        	extractedPaths.add(findShortestPaths(graph, trigger, theme));
					    	//extractedPaths.add(findAllPaths(graph, trigger, theme));
					    } 
					    List<DirectedGraph<Vertex, Edge>> results = computePathUnion(extractedPaths);
					    for(DirectedGraph<Vertex, Edge> path : results) {
	                		EventRule pattern = new EventRule(path, event, sentence, pmid, "Theme"); 
	                		eventRulesOfSentence.add(pattern);
					    } 
					    extractedPathsCombined.add(results);
						//has cause argument
						if(event.hasCause()) {
							Vertex cause;
							//no subevent
							if(event.getEventCause().charAt(0) == 'T') {
								cause = sentence.getProteins().get(event.getEventCause()).getGraphNode();
						    }
							//with subevent
							else {
								String trigger = sentence.getEvents().get(event.getEventCause()).getEventTrigger();
								cause = sentence.getTriggers().get(trigger).getTriggerCenterNode();    	
							}
							triggers = sentence.getTriggers().get(event.getEventTrigger()).getTriggerNodes();
						    extractedPaths = new ArrayList<List<DirectedGraph<Vertex, Edge>>>();
						    for(Vertex trigger : triggers) {
	                        	extractedPaths.add(findShortestPaths(graph, trigger, cause));
						    	//extractedPaths.add(findAllPaths(graph, trigger, cause)); 
						    } 
						    results = computePathUnion(extractedPaths);
						    for(DirectedGraph<Vertex, Edge> path : results) {
		                		EventRule pattern = new EventRule(path, event, sentence, pmid, "Cause");
		                		eventRulesOfSentence.add(pattern);
						    }	
						    extractedPathsCombined.add(results);
						}
						List<DirectedGraph<Vertex, Edge>> resultsFinal;
						if(event.hasCause())
							resultsFinal = computePathUnion(extractedPathsCombined);
						else resultsFinal = extractedPathsCombined.get(0);
					    
						for(DirectedGraph<Vertex, Edge> path : resultsFinal) {
	                		EventRule pattern = new EventRule(path, event, sentence, pmid);
	                		eventRulesOfSentence.add(pattern);	
					    }
					}
				}
				//set event rules of the sentence
				sentence.setEventRulesOfSentence(eventRulesOfSentence);
				for(EventRule pattern : eventRulesOfSentence) {
					if(allEventRules.containsKey(pattern.getEventCategory())) {
						allEventRules.get(pattern.getEventCategory()).add(pattern);
					}
					else {
					    List<EventRule> temp = new ArrayList<EventRule>(); 
					    temp.add(pattern);
						allEventRules.put(pattern.getEventCategory(), temp);
					}    
				}
			}	
		}
	}
	
	/**
	 * remove isomorphic paths for each event type using ESM
	 */
	private void removeIsomorphicPaths() {
		for(String eventType : allEventRules.keySet()) {
			System.out.println("removing isomorphism from " + eventType);
	    	//deal with isomorphic dependency graphs of event rules
	    	//first pairwise scan to set removal sign
	    	for(int i=0; i<allEventRules.get(eventType).size()-1; i++) {
	    	    //no need to attempt the path with removal sign true, for efficiency
	    		if( allEventRules.get(eventType).get(i).getRemovalSign() )
	    		    continue;
	    		for(int j = i+1; j < allEventRules.get(eventType).size(); j++) {
	    			//no need to attempt the path with removal sign true, for efficiency
		    		if( allEventRules.get(eventType).get(j).getRemovalSign() )
		    		    continue;
		    		//make sure when regulation-related events are compared, they have same number of arguments 
		    		if(allEventRules.get(eventType).get(i).getEventCategory().endsWith("egulation") &&		
		    		   !( (allEventRules.get(eventType).get(i).hasTheme() == allEventRules.get(eventType).get(j).hasTheme()) && 
		    		      (allEventRules.get(eventType).get(i).hasCause() == allEventRules.get(eventType).get(j).hasCause()) 
		    		    ) )
		    			continue;
	    	    	// if path i's length is equal to path j's
	    	    	if( allEventRules.get(eventType).get(i).getGraph().getVertexCount() == 
	    	    		    allEventRules.get(eventType).get(j).getGraph().getVertexCount() ) {
	    	    		CustomESM esm = new CustomESM(allEventRules.get(eventType).get(i).getGraph(), 
	    	    				allEventRules.get(eventType).get(j).getGraph());
	    	    	    //set removal sign true for the isomorphic path 
	    	    	    if(esm.isGraphIsomorphism()) {
	    	    	    	allEventRules.get(eventType).get(j).setRemovalSign(true);
	    	    	    	/*
	    	    	    	System.out.println("graph isomorphic");
	    	    	    	System.out.println(allEventRules.get(eventType).get(i).getPMID() + " " + 
	    	    	    			allEventRules.get(eventType).get(i).getSentenceID() + " " + allEventRules.get(eventType).get(i).getGoldEvent().getEventID() + " " + 
	    	    	    			allEventRules.get(eventType).get(i));
	    	    	    	System.out.println(allEventRules.get(eventType).get(j).getPMID() + " " + 
	    	    	    			allEventRules.get(eventType).get(j).getSentenceID() + " " + allEventRules.get(eventType).get(j).getGoldEvent().getEventID() + " " +
	    	    	    			allEventRules.get(eventType).get(j));*/
	    	    	    }	
	    	    	}	
	    	    }
	    	}
	    	//second scan to present paths with removal sign false
	    	for(int i=0; i<allEventRules.get(eventType).size(); i++) {
	    		if( !allEventRules.get(eventType).get(i).getRemovalSign() ) {
	    			if(eventRulesWithoutIsomorphism.containsKey(eventType)) {
	    				eventRulesWithoutIsomorphism.get(eventType).add(allEventRules.get(eventType).get(i));
					}
					else {
					    List<EventRule> temp = new ArrayList<EventRule>(); 
					    temp.add(allEventRules.get(eventType).get(i));
					    eventRulesWithoutIsomorphism.put(eventType, temp);
					}   
	    		}
	    	}
		}
	}
	
	/**
	 * write the extracted event rules to files 
	 * in terms of the event type
	 */
	private void writeEventRulesToFiles() {
		for(String eventType : eventRulesWithoutIsomorphism.keySet()) {
			System.out.println("Writing " + eventType + " with " + 
					eventRulesWithoutIsomorphism.get(eventType).size() + " rules");
			//specify where to write
			//set relative path
			String relativePath = "resources/rules/";
			//check the specified context depth
			String outputFileName = relativePath + eventType + ".rule";
			File outputFile = new File(outputFileName);
	    	outputFile.getParentFile().mkdirs();
	    	BufferedWriter output;
			try {
				output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8, 
	                    WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
				int count = 0;
			    for(EventRule rule : eventRulesWithoutIsomorphism.get(eventType)) {
			    	output.write( ++count + ":\t"+ rule + "\n" );
			    }
			    output.close();	
			} catch (FileNotFoundException e) {
				throw new RuntimeException("Unable to open the output file: "
						+ outputFileName, e);
			} catch (IOException e) {
				throw new RuntimeException("Unable to process the output file: ", e);
			} 
		}
	}
	
	/**
	 * compute path union
	 * @param paths
	 * @return
	 */
	public static List<DirectedGraph<Vertex, Edge>> computePathUnion(List<List<DirectedGraph<Vertex, Edge>>> paths) {
		List<DirectedGraph<Vertex, Edge>> unions = new ArrayList<DirectedGraph<Vertex, Edge>>();
		DirectedGraph<Vertex, Edge> path = new DirectedSparseGraph<Vertex, Edge>();
    	List< DirectedGraph<Vertex, Edge> > pathsTemp = new ArrayList< DirectedGraph<Vertex, Edge> >();
    	unions = computePathUnion(paths, pathsTemp, path);	
		return unions;
	}
	
	private static List<DirectedGraph<Vertex, Edge>> computePathUnion(List<List<DirectedGraph<Vertex, Edge>>> paths, 
			List<DirectedGraph<Vertex, Edge>> pathUnion, DirectedGraph<Vertex, Edge> path){
		//check the limit on the number of all the paths retrieved, to avoid combinatorial explosion 
		if(pathUnion.size() == 50)
			return pathUnion;
		if(paths.isEmpty())
			pathUnion.add(path);
		else {
			List<DirectedGraph<Vertex, Edge>> list = paths.get(0);
			paths.remove(0);
			for(DirectedGraph<Vertex, Edge> p : list) {
				DirectedGraph<Vertex, Edge> current = new DirectedSparseGraph<Vertex, Edge>();
				//use path to update current; copy the graph
	        	for(Vertex v: path.getVertices()) {
	        		current.addVertex(v);
	        		for(Edge e : path.getIncidentEdges(v)) {
	    				current.addEdge(e, e.getGovernor(), e.getDependent());	
	    			}
	        	}	
	        	//use p to update current to get the graph union
	        	for(Vertex v: p.getVertices()) {
	        		current.addVertex(v);
	        		for(Edge e : p.getIncidentEdges(v)) {
	    				current.addEdge(e, e.getGovernor(), e.getDependent());	
	    			}
	        	}	
			    List<List<DirectedGraph<Vertex, Edge>>> m = new ArrayList<List<DirectedGraph<Vertex, Edge>>>(paths);
			    pathUnion = computePathUnion(m, pathUnion, current);
			}
		}
		return pathUnion;
	}
	
	/**
	 * Retrieve the shortest paths between two graph nodes 
	 * This is the public interfact of the shortest paths function
	 * based on the calcuated shortest distance score via the Dijkstra algorithm
	 * @param graph : input graph
	 * @param source : source node
	 * @param target : target node
	 * @return vertex-based shortest paths
	 */
	public static List<DirectedGraph<Vertex, Edge>> findShortestPaths (DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target){
		List<DirectedGraph<Vertex, Edge>> shortestPathGraphs = new ArrayList<DirectedGraph<Vertex, Edge>>();
		List<List<Vertex>> shortestPaths = null;
		//compute distance between two start nodes
	    int dist = shortestDistance(graph, source, target);
	    //valid distance
	    if(dist != -1) {
	    	//compute the shortest paths between two nodes
		    shortestPaths = findShortestPaths(graph, source, target, dist);	
	    }
	    if(shortestPaths != null) {
	    	shortestPathGraphs = transformPathsIntoGraphs(shortestPaths, graph);
	    }
	    return shortestPathGraphs;
	}
	
	/**
	 * Calculate shortest distance between two nodes in a graph using Dijkstra's algorithm
	 * @param graph : input graph
	 * @param source : source node
	 * @param target : target node
	 * @return shortest distance in integer
	 */
	private static int shortestDistance (DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target){
		//adding bi-directional edges to the graph for calculating the shortest path on undirected graph
		DirectedGraph<Vertex, Edge> bidirectedGraph = new DirectedSparseGraph<Vertex, Edge>();
        for(Vertex v : graph.getVertices()){ 
			// add nodes to the directed graph
			bidirectedGraph.addVertex(v); 
			for(Edge e : graph.getIncidentEdges(v)) { 
				// add one-way edges to the directed graph
				bidirectedGraph.addEdge(e, e.getGovernor(), e.getDependent());	
				// add the-other-way edges to the directed graph
				Edge eReverse = new Edge(e.getDependent(), e.getLabel(), e.getGovernor());		    
				bidirectedGraph.addEdge(eReverse, e.getDependent(), e.getGovernor()); 
			}
		}
		//compute the shortest distance between source and destination via Dijkstra's algorithm
		DijkstraShortestPath<Vertex, Edge> dijkstra = new DijkstraShortestPath<Vertex, Edge>(bidirectedGraph);
		int shortestDistance;
		Number value = dijkstra.getDistance(source, target);
		if(value != null)
		    shortestDistance = value.intValue();
		else
			shortestDistance = -1;

		return shortestDistance;
	}
	
	/**
	 * Retrieve the shortest paths between two graph nodes 
	 * based on the calcuated shortest distance score via the Dijkstra algorithm
	 * @param graph : input graph
	 * @param source : source node
	 * @param target : target node
	 * @param shortestDistance : shortest distance between two nodes, an integer value
	 * @return vertex-based shortest paths
	 */
	private static List<List<Vertex>> findShortestPaths (DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target, int shortestDistance){
		List<List<Vertex>> paths = new ArrayList<List<Vertex>>();
		List<Vertex> visited = new ArrayList<Vertex>();
		visited.add(source);
		paths = findAllPaths(graph, visited, paths, source, target);
		List<List<Vertex>> shortestPaths = new ArrayList<List<Vertex>>(); 
		for(List<Vertex> path : paths) {
		    if(path.size() == shortestDistance + 1)
		    	shortestPaths.add(path);
		}
		return shortestPaths;
	}
	
	/**
	 * Recursively retrieve all vertex-based acyclic paths between two nodes
	 * @param graph : input graph
	 * @param visited : visited nodes
	 * @param paths : retrieved paths
	 * @param currentNode : current node
	 * @param target : target node
	 * @return vertex-based paths
	 */
	public static List<DirectedGraph<Vertex, Edge>> findAllPaths(DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target) {
		List<DirectedGraph<Vertex, Edge>> shortestPathGraphs = new ArrayList<DirectedGraph<Vertex, Edge>>();
		List<List<Vertex>> paths = new ArrayList<List<Vertex>>();
		List<Vertex> visited = new ArrayList<Vertex>();
		visited.add(source); 
		paths = findAllPaths(graph, visited, paths, source, target); 
		shortestPathGraphs = transformPathsIntoGraphs(paths, graph);
		return shortestPathGraphs;
	}
	
	/**
	 * Recursively retrieve all vertex-based acyclic paths between two nodes
	 * @param graph : input graph
	 * @param visited : visited nodes
	 * @param paths : retrieved paths
	 * @param currentNode : current node
	 * @param target : target node
	 * @return vertex-based paths
	 */
	private static List<List<Vertex>> findAllPaths(DirectedGraph<Vertex, Edge> graph, List<Vertex> visited, List<List<Vertex>> paths, Vertex currentNode, Vertex target) {
		List<List<Vertex>> currentPaths = new ArrayList<List<Vertex>>(paths);
		if(currentNode.equals(target)) {
		    currentPaths.add(visited);	
		}
		else {
			List<Vertex> adjacentNodes = new ArrayList<Vertex>(graph.getNeighbors(currentNode));
			for(Vertex node : adjacentNodes) {
				if(visited.contains(node))
					continue;
				List<Vertex> temp = new ArrayList<Vertex>(visited);
				temp.add(node);
				currentPaths = findAllPaths(graph, temp, currentPaths, node, target);
			}
		}
		
		return currentPaths;
	}
	
	/**
	 * Transform vertex-based paths into directed graphs
	 * This is to calculate graph isomorphism in the later process
	 * @param shortestPaths : multiple shortest paths
	 * @param graph : dependency graph
	 * @return directed graphs to record paths
	 */
	public static List<DirectedGraph<Vertex, Edge>> transformPathsIntoGraphs(List<List<Vertex>> shortestPaths, DirectedGraph<Vertex, Edge> graph) {
		List<DirectedGraph<Vertex, Edge>> shortestPathGraphs = new ArrayList<DirectedGraph<Vertex, Edge>>();	
		for(List<Vertex> shortestPath : shortestPaths) {
			List< DirectedGraph<Vertex, Edge> > paths = new ArrayList< DirectedGraph<Vertex, Edge> >();
			DirectedGraph<Vertex, Edge> path = new DirectedSparseGraph<Vertex, Edge>();
	    	List< DirectedGraph<Vertex, Edge> > pathsTemp = new ArrayList< DirectedGraph<Vertex, Edge> >();
	    	paths = combineMatching(graph, shortestPath, pathsTemp, path);	
	    	shortestPathGraphs.addAll(paths);
		}
		return shortestPathGraphs;
	}
	
	/**
	 * Generate paths with combinations of various dependency edge labels
	 * Store each path into a graph (linear dependency path)
	 * @param graph : dependency graph
	 * @param vertices : vertices involved in a path
	 * @param paths : list of graphs that record paths
	 * @param path : a graph that records a path
	 * @return
	 */
	private static List<DirectedGraph<Vertex, Edge>> combineMatching (DirectedGraph<Vertex, Edge> graph, List<Vertex> vertices, 
			List<DirectedGraph<Vertex, Edge>> paths, DirectedGraph<Vertex, Edge> path){
		if(vertices.size() == 1){
			paths.add(path); 
	    }
	    else {
		    Vertex m = vertices.get(0);
		    Vertex n = vertices.get(1);
	        vertices.remove(0); 
	        Set<Edge> edges = new HashSet<Edge>();
	        edges.addAll(graph.findEdgeSet(m, n));
	        edges.addAll(graph.findEdgeSet(n, m));
	        for(Edge edge : edges){
	        	DirectedGraph<Vertex, Edge> current = new DirectedSparseGraph<Vertex, Edge>();
	        	//use path to update current; copy the graph
	        	for(Vertex v: path.getVertices()) {
	        		current.addVertex(v);
	        		for(Edge e : path.getIncidentEdges(v)) {
	    				current.addEdge(e, e.getGovernor(), e.getDependent());	
	    			}
	        	}	
	        	//for(Edge e: path.getEdges())
	        	//	current.addEdge(e, path.getIncidentVertices(e));

	        	//update current
	        	current.addVertex(m); current.addVertex(n);
	        	current.addEdge(edge, m, n);
	        	List<Vertex> v = new ArrayList<Vertex>(vertices);
	        	paths = combineMatching(graph, v, paths, current);
	        }
	    }
		return paths;
	}
}
