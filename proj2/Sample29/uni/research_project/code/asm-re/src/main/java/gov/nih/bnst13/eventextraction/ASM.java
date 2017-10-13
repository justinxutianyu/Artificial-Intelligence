package gov.nih.bnst13.eventextraction;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.TreeMap;
import org.apache.commons.collections15.CollectionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gov.nih.bnst13.patternlearning.EventRule;
import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst13.preprocessing.combine.training.ReadSingleSentenceOutput;
import gov.nih.bnst13.preprocessing.dp.Edge;
import gov.nih.bnst13.preprocessing.dp.Vertex;
import edu.uci.ics.jung.algorithms.shortestpath.DijkstraShortestPath;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;


/**	
 * <p>ASM: Approximate Subgraph Matching (ASM) to detect approximate subgraph isomorphism between dependency graphs</p> 
 * 
 *  @author Implemented by Haibin Liu
 */

public class ASM {
	private static final Logger LOG = LoggerFactory.getLogger(ASM.class);
	
	
	/** subgraph to be matched (normally smaller graph) */
	private DirectedGraph<Vertex, Edge> subgraph = null;
	/** graph to be matched (normally bigger graph) */
	private DirectedGraph<Vertex, Edge> graph = null;
	/** startnode of subgraph for matching (from which subgraph node to start the matching process) */
	private Vertex subgraphStartNode = null;
	/** a set of startnodes of graph for matching */
	private List<Vertex> graphStartNodes = null;
	/** the thresholds of the subgraph distance, SUBGRAPH_DISTANCE_THRESHOLD */
	private double SUBGRAPH_DISTANCE_THRESHOLD; 
	/** the weight of the structural subgraph distance */
	private int structureWeight;
	/** the weight of the label subgraph distance */
	private int labelWeight;
	/** the weight of the directionality subgraph distance */
	private int directionalityWeight;
	/** cache for subgraph shortest distance */
	private Map<Vertex, Map<Vertex, Integer>> subgraphDistanceCache;
    /** cache for subgraph shortest paths */
	private Map<Vertex, Map<Vertex, List<List<Vertex>>>> subgraphPathsCache;
	/** cache for graph shortest distance */
	private Map<Vertex, Map<Vertex, Integer>> graphDistanceCache;
    /** cache for graph shortest paths */
	private Map<Vertex, Map<Vertex, List<List<Vertex>>>> graphPathsCache;
	/** event rule that corresponds to the subgraph */
	private EventRule rule; 
	
	/**
	 * Constructor to initialize the subgraph and graph and 
	 * specify the start node of the subgraph and the set of start nodes of the graph 
	 * @param subgraph : subgraph (supposed to be smaller)
	 * @param graph : graph (supposed to be bigger)
	 */
	public ASM (DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph, 
			int subgraphDistanceThreshold, int[] subgraphWeights) {
		this.graph = graph;
		this.subgraph = subgraph;
		//set the startnode of subgraph 
	    subgraphStartNode = getRandomStartNode( new ArrayList<Vertex>(subgraph.getVertices()) );
	    graphStartNodes = new ArrayList<Vertex>(graph.getVertices());
	    
	    SUBGRAPH_DISTANCE_THRESHOLD = subgraphDistanceThreshold;
	    structureWeight = subgraphWeights[0];
	    labelWeight = subgraphWeights[1];
	    directionalityWeight = subgraphWeights[2];
	    
		subgraphDistanceCache = new HashMap<Vertex, Map<Vertex, Integer>>();
		subgraphPathsCache = new HashMap<Vertex, Map<Vertex, List<List<Vertex>>>>();
		graphDistanceCache = new HashMap<Vertex, Map<Vertex, Integer>>();
		graphPathsCache = new HashMap<Vertex, Map<Vertex, List<List<Vertex>>>>();
		
		/** computes pairwise shortest distance and paths of the subgraph */
		computeSubgraphPairwiseShortestDistanceAndPaths(subgraph);
	}
	
	/**
	 * shared task specific constructor
	 * @param rule
	 * @param sentence
	 * @param subgraphDistanceThreshold
	 * @param subgraphWeights
	 */
	public ASM (EventRule rule, AnnotatedSentence sentence, 
			int subgraphDistanceThreshold, int[] subgraphWeights) { 
		this.rule = rule;
		this.graph = sentence.getDependencyGraph().getGraph();
		this.subgraph = rule.getGraph();
		//set the startnode of subgraph 
	    subgraphStartNode = getRandomStartNode( new ArrayList<Vertex>(subgraph.getVertices()) );
	    graphStartNodes = new ArrayList<Vertex>(graph.getVertices());
	    
	    SUBGRAPH_DISTANCE_THRESHOLD = subgraphDistanceThreshold;
	    structureWeight = subgraphWeights[0];
	    labelWeight = subgraphWeights[1];
	    directionalityWeight = subgraphWeights[2];
	    
		subgraphDistanceCache = rule.getDistanceCache();
		subgraphPathsCache = rule.getPathsCache();
		graphDistanceCache = new HashMap<Vertex, Map<Vertex, Integer>>();
		graphPathsCache = new HashMap<Vertex, Map<Vertex, List<List<Vertex>>>>();
	}
	
	/**
	 * randomly choose the start node of the subgraph (default setting)
	 * @param subgraphNodes
	 * @return start node of the subgraph
	 */
	private Vertex getRandomStartNode( List<Vertex> subgraphNodes) {
		//Create random class object
		Random random = new Random(); 
		//Generate a random number (index) with the size of the list being the maximum
		int randomNumber = random.nextInt(subgraphNodes.size()); 
		return subgraphNodes.get(randomNumber); 
	}
	
	public Map<Double, List< Map<Vertex, Vertex>>> getApproximateSubgraphMatchingMatches() {
		//structure containing eventual matching results
		Map<Double, List<Map<Vertex,Vertex>>> matchings = new TreeMap<Double, List< Map<Vertex, Vertex>>>();
    	
    	//sanity check #1: quick check to detect non-matching graph pairs
    	if(subgraph.getVertexCount() > graph.getVertexCount()) {
    		/*System.err.println("The size of the subgraph: " + 
					subgraph.getVertexCount() + " is bigger than the size of the graph " + 
					graph.getVertexCount() + ". Please check."); */ 
    		return matchings;
    	}	
    	
    	//sanity check #2: make sure injective matches exist between subgraph nodes and graph nodes
    	for(Vertex subgraphNode : subgraph.getVertices()) {
    		boolean flag = false;
	    	for(Vertex graphNode : graph.getVertices()) {
	    		if( matchNodeContent(subgraphNode, graphNode) ) {
	    			LOG.trace("Nodes {} and {} match", subgraphNode, graphNode);
	    			flag = true;
	    			break;
	    		} else {
	    			LOG.trace("Nodes {} and {} do not match (comparing {} vs {})",
	    					subgraphNode, graphNode, subgraphNode.getCompareForm(), graphNode.getCompareForm());
	    		}
	    	}
	    	if(!flag) {
	    		LOG.debug("No raw node matches between subgraph vertices {} and graph vertices {}", 
	    				subgraph.getVertices(), graph.getVertices());  
	    		return matchings;
	    	}
    	}
    	
    	LOG.trace("Start nodes are {}", graphStartNodes);
    	for(Vertex graphStartNode : graphStartNodes) { 
    		LOG.trace("Checking start node {}", graphStartNode);
    	    if( !matchNodeContent(subgraphStartNode, graphStartNode) )	
    	    	continue;
    	    Map<Vertex, Set<Vertex>> injectiveMatches = new HashMap<Vertex, Set<Vertex>>();
    	    Set<Vertex> matchedGraphStartNodes= new HashSet<Vertex>();
    	    matchedGraphStartNodes.add(graphStartNode);
    	    injectiveMatches.put(subgraphStartNode, matchedGraphStartNodes);
    	    List< Map<Vertex, Vertex> > candidateMatchings = new ArrayList< Map<Vertex, Vertex> >();
    	    
    	    for(Vertex subgraphNode : subgraph.getVertices()) {
    	    	LOG.trace("Checking subgraph node {}", subgraphNode);
    	    	if(subgraphNode.equals(subgraphStartNode))
    	    		continue;
    	    	Set<Vertex> matchedGraphNodes= new HashSet<Vertex>();
    	    	for(Vertex graphNode : graph.getVertices()) {
    	    		if(graphNode.equals(graphStartNode))
    	    			continue;
    	    		if( matchNodeContent(subgraphNode, graphNode) ) {
    	    			matchedGraphNodes.add(graphNode);
    	    		}
    	    	}
    	    	if(matchedGraphNodes.isEmpty()) {
    	    		LOG.trace("No matched graph nodes for {}", subgraphNode);
    	    		break;
    	    	}
    	    	LOG.trace("Subgraph node {} has matches {}", subgraphNode, matchedGraphNodes);
    	    	injectiveMatches.put(subgraphNode, matchedGraphNodes);
    	    }
    	    if( injectiveMatches.size() == subgraph.getVertexCount() ) {
    	    	Map<Vertex, Vertex> sequence = new HashMap<Vertex, Vertex>();
    	    	List< Map<Vertex, Vertex> > candidateMatchingsTemp = new ArrayList< Map<Vertex, Vertex> >();
    	    	//set the limit of matching combinations
    	    	int combinationLimit = 10000;
    	    	candidateMatchings = combineMatching(injectiveMatches, candidateMatchingsTemp, sequence, combinationLimit);
    	    	LOG.trace("Found {} graph matches", candidateMatchings.size());
    	    	for(Map<Vertex, Vertex> cm : candidateMatchings) {
    	    		double distance = subgraphDistance(cm, subgraph, graph);
    	    		if(distance >= 0 && distance <= SUBGRAPH_DISTANCE_THRESHOLD ) {
    	    			if(matchings.containsKey(distance))
    	    			    matchings.get(distance).add(cm);
    	    			else {
    	    				List<Map<Vertex,Vertex>> temp = new ArrayList<Map<Vertex,Vertex>>();
    	    				temp.add(cm);
    	    				matchings.put(distance, temp);
    	    			}
    	    		}
    	    		graphDistanceCache.clear(); 
    	    		graphPathsCache.clear();
    	    	}
    	    }
    	}
    	return matchings;
	}
	
	/**
	 * determine if a subgraph node can match with a graph node
	 * based on different matching features
	 * @param subgraphNode
	 * @param graphNode
	 * @return
	 */
	private boolean matchNodeContent(Vertex subgraphNode, Vertex graphNode) { 
		boolean canMatch = false;
		// the matching criteria can be extended, 
		// i.e., word can be lemma, and tag can be generalized tag
		// ontological resources can be also imported here for node matching
		if( subgraphNode.getCompareForm().equals(graphNode.getCompareForm()))
			   canMatch = true;
		
		return canMatch;
	}
	
	
	/**
	 * determine if a subgraph node can match with a graph node
	 * based on different matching features
	 * @param subgraphNode
	 * @param graphNode
	 * @return
	 */
	/*private boolean matchNodeContent(Vertex subgraphNode, Vertex graphNode) { 
		boolean canMatch = false;
		// the matching criteria can be extended, 
		// i.e., word can be lemma, and tag can be generalized tag
		// ontological resources can be also imported here for node matching
		if( subgraphNode.getCompareForm().equals(graphNode.getCompareForm()))
			   canMatch = true;
		else if(!subgraphNode.isProtein() && subgraphNode.isTrigger() && !graphNode.getCompareForm().startsWith("bio_entity") &&  
				subgraphNode.getGeneralizedPOS().equals(graphNode.getGeneralizedPOS())) {
			if(EventExtraction.dsm.containsKey(subgraphNode.getCompareForm()) && EventExtraction.dsm.containsKey(graphNode.getCompareForm())) {
				//System.out.println("checking " + subgraphNode + " " + graphNode);
				if(EventExtraction.dsmCache.containsKey(subgraphNode.getCompareForm() + " " + graphNode.getCompareForm())) {
				    canMatch = EventExtraction.dsmCache.get(subgraphNode.getCompareForm() + " " + graphNode.getCompareForm());
				}
				else if(EventExtraction.dsmCache.containsKey(graphNode.getCompareForm() + " " + subgraphNode.getCompareForm())) {
				    canMatch = EventExtraction.dsmCache.get(graphNode.getCompareForm() + " " + subgraphNode.getCompareForm());
				}
				else {
					//Set<String> intersection = new HashSet<String>(EventExtraction.dsm.get(subgraphNode.getCompareForm()));
					//intersection.retainAll(EventExtraction.dsm.get(graphNode.getCompareForm()));	
					//if(!intersection.isEmpty())
					//	canMatch = true;
					//intersection.clear(); intersection = null;
					Set<String> originalModel = EventExtraction.dsm.get(graphNode.getCompareForm());
					Set<String> updatedModel = new HashSet<String>();
					for(String token : originalModel) {
						boolean flag = false;
						for(String category : EventExtraction.triggerHash.keySet()) {
							if(!category.equals(rule.getEventCategory())) {
								for(Vertex v : EventExtraction.triggerHash.get(category)) {
									if(v.getCompareForm().equals(token))
										flag = true; break;
								}
							}
							if(flag) break;
						}
						if(!flag) updatedModel.add(token);
					}
					if(updatedModel.contains(subgraphNode.getCompareForm()))
						canMatch = true;
					EventExtraction.dsmCache.put(subgraphNode.getCompareForm() + " " + graphNode.getCompareForm(), canMatch);
					EventExtraction.dsmCache.put(graphNode.getCompareForm() + " " + subgraphNode.getCompareForm(), canMatch);
				}
				//if(canMatch)
				//	EventExtraction.dsmTrigger.put(subgraphNode.getCompareForm(), 
				//			new ArrayList<String>(EventExtraction.dsm.get(subgraphNode.getCompareForm())).get(0));
			}
		}
		//System.out.println("checking " + subgraphNode + " " + graphNode + " " + canMatch);
		return canMatch;
	}*/
	
	private static List< Map<Vertex, Vertex> > combineMatching (Map<Vertex, Set<Vertex>> injectiveMatches, 
			List<Map<Vertex, Vertex>> candidateMatchings, Map<Vertex, Vertex> sequence, int combinationLimit){
		//check limit
		if(candidateMatchings.size() > combinationLimit) 
			return candidateMatchings;
		
		if(injectiveMatches.isEmpty()){
	    	candidateMatchings.add(sequence); 
	    }
	    else {
		    Vertex n = (Vertex) CollectionUtils.get(injectiveMatches.keySet(), 0);
	        Set<Vertex> set = injectiveMatches.remove(n); 
	        for(Vertex i : set){
	        	Map<Vertex, Vertex> s = new HashMap<Vertex, Vertex>(sequence);	        	
	        	//put in a new mapping n->i
	        	s.put(n, i);
	        	//check if element in s is unique
	        	if(s.values().size() != new HashSet<Vertex>(s.values()).size())
	        	    continue;
	        	Map<Vertex, Set<Vertex>> m = new HashMap<Vertex, Set<Vertex>>(injectiveMatches);
	        	candidateMatchings = combineMatching(m, candidateMatchings, s, combinationLimit);
	        }
	    }
		return candidateMatchings;
	}
	
	private double subgraphDistance (Map<Vertex, Vertex> cm, DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph) {
		double distance = -1; 

		//threshold should be checked for each subgraphDistance component, 
		//because there is no need to proceed if one component exceeds the threshold	
		double structDist = structDist(cm, subgraph, graph); 
		if(structDist == -1)
			return distance;
			//throw new RuntimeException("The structural distance: "
			//		+ structDist + " is not valid. Please check.");
		if(structureWeight * structDist > SUBGRAPH_DISTANCE_THRESHOLD)
			return distance;
		
		double labelDist = labelDist(cm, subgraph, graph); 		
		if(labelDist == -1)
			return distance;
			//throw new RuntimeException("The label distance: "
			//		+ labelDist + " is not valid. Please check.");
		if(labelWeight * labelDist > SUBGRAPH_DISTANCE_THRESHOLD || 
				structureWeight * structDist + labelWeight * labelDist > SUBGRAPH_DISTANCE_THRESHOLD )
			return distance;
		
		double directionalityDist = directionalityDist(cm, subgraph, graph);
		if(directionalityDist == -1)
			return distance;
			//throw new RuntimeException("The directionality distance: "
			//		+ directionalityDist + " is not valid. Please check.");
		if(directionalityWeight * directionalityDist > SUBGRAPH_DISTANCE_THRESHOLD)
			return distance;

		distance = structureWeight * structDist + labelWeight * labelDist + directionalityWeight * directionalityDist; 
		
		//System.out.println(distance + " "+ structDist + " " + labelDist + " " + directionalityDist);
		return distance;
	}
	
	private double structDist (Map<Vertex, Vertex> cm, DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph) {
	    double structDist = 0;
	    double normalizedStructDist = -1;
	    double sumSubgraphDist = 0;
	    double sumGraphDist = 0;
	    List<Vertex> cmKeys = new ArrayList<Vertex>(cm.keySet()); 
	    for(int i = 0; i < cmKeys.size() - 1; i++){
	    	for(int j = i+1; j < cmKeys.size(); j++){ 
	    		int subgraphDist;
	    		int graphDist;
	    		List<List<Vertex>> graphPaths;
                
                subgraphDist = subgraphDistanceCache.get(cmKeys.get(i)).get(cmKeys.get(j));
                
	    		//retrieve or compute pairwise shortest distance and paths of graph
    		    if( graphDistanceCache.containsKey( cm.get(cmKeys.get(i)) ) && 
		    		graphDistanceCache.get( cm.get(cmKeys.get(i)) ).containsKey( cm.get(cmKeys.get(j)) ) ) {
	    			
	    			graphDist = graphDistanceCache.get(cm.get(cmKeys.get(i))).get(cm.get(cmKeys.get(j)));
	    			graphPaths = graphPathsCache.get(cm.get(cmKeys.get(i))).get(cm.get(cmKeys.get(j)));
		    	}
	    		else { 
	    		    //compute paths for graph
	    		    graphPaths = findAllPaths(graph, cm.get(cmKeys.get(i)), cm.get(cmKeys.get(j)));
	    		    //no path found
	    		    if(graphPaths.size() == 0)
		    		    return normalizedStructDist; 
	    		    //choose ones that lead to minimum difference with pairwise distance between nodes in the corresponding subgraph
	    		    TreeMap<Integer, List<List<Vertex>>> sorted = new TreeMap<Integer, List<List<Vertex>>>();
	    		    for(List<Vertex> path : graphPaths) {
	    			    int difference = Math.abs(path.size() - 1 - subgraphDist);
	    		    	if(sorted.containsKey(difference))
	    			    	sorted.get(difference).add(path);
	    		    	else {
	    		    		List<List<Vertex>> temp = new ArrayList<List<Vertex>>();
	    		    		temp.add(path);
	    		    		sorted.put(difference, temp);
	    		    	}
	    			}
	    		    graphPaths = sorted.get(sorted.firstKey());
	    		    //put into paths cache for graph
		    		if(graphPathsCache.containsKey(cm.get(cmKeys.get(i)))) {
		    			graphPathsCache.get(cm.get(cmKeys.get(i))).put(cm.get(cmKeys.get(j)), graphPaths);
		    		}
		    		else {
		    			Map<Vertex, List<List<Vertex>>> temp = new HashMap<Vertex, List<List<Vertex>>>();
			    		temp.put(cm.get(cmKeys.get(j)), graphPaths);
		    			graphPathsCache.put(cm.get(cmKeys.get(i)), temp);
		    		}
		    		//compute distance for graph
	    		    graphDist = sorted.firstKey() + subgraphDist;	    		
	    		    //put into distance cache for graph
	    		    if(graphDistanceCache.containsKey(cm.get(cmKeys.get(i)))) {
		    			graphDistanceCache.get(cm.get(cmKeys.get(i))).put(cm.get(cmKeys.get(j)), graphDist);
		    		}
		    		else {
		    			HashMap<Vertex, Integer> temp = new HashMap<Vertex, Integer>();
			    		temp.put(cm.get(cmKeys.get(j)), graphDist);
		    			graphDistanceCache.put(cm.get(cmKeys.get(i)), temp);
		    		}
	    		}

	    		structDist += Math.abs(subgraphDist - graphDist);
	    		
	    		sumSubgraphDist += subgraphDist;
	    		sumGraphDist += graphDist;
		    }
	    }
	    if(sumSubgraphDist == 0 || sumGraphDist == 0) {
	    	normalizedStructDist = 0;
			//throw new RuntimeException("The sum of the structural distance: "
				//	+ sumSubgraphDist + " " + sumGraphDist + " is not valid. Please check.");
	    }	
	    else 
	    	normalizedStructDist = structDist / (sumSubgraphDist + sumGraphDist);
        
	    return normalizedStructDist;
	}
	
	/*
	private double structDist (Map<Vertex, Vertex> cm, DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph) {
	    double structDist = 0;
	    double normalizedStructDist = -1;
	    double sumSubgraphDist = 0;
	    double sumGraphDist = 0;
	    List<Vertex> cmKeys = new ArrayList<Vertex>(cm.keySet()); 
	    for(int i = 0; i < cmKeys.size() - 1; i++){
	    	for(int j = i+1; j < cmKeys.size(); j++){ 
	    		int subgraphDist;
	    		int graphDist;
	    		List<List<Vertex>> graphPaths;
                
                subgraphDist = subgraphDistanceCache.get(cmKeys.get(i)).get(cmKeys.get(j));
                
	    		//retrieve or compute pairwise shortest distance and paths of graph 
    		    if( graphDistanceCache.containsKey( cm.get(cmKeys.get(i)) ) && 
		    		graphDistanceCache.get( cm.get(cmKeys.get(i)) ).containsKey( cm.get(cmKeys.get(j)) ) ) {
	    			
	    			graphDist = graphDistanceCache.get(cm.get(cmKeys.get(i))).get(cm.get(cmKeys.get(j)));
	    			graphPaths = graphPathsCache.get(cm.get(cmKeys.get(i))).get(cm.get(cmKeys.get(j)));
		    	}
	    		else { 
	    			//compute distance for graph
	    		    graphDist = shortestDistance(graph, cm.get(cmKeys.get(i)), cm.get(cmKeys.get(j)));	    		
	    		    if(graphDist == -1)
		    		    return normalizedStructDist; 
	    		    
	    		    //put into distance cache for graph
	    		    if(graphDistanceCache.containsKey(cm.get(cmKeys.get(i)))) {
		    			graphDistanceCache.get(cm.get(cmKeys.get(i))).put(cm.get(cmKeys.get(j)), graphDist);
		    		}
		    		else {
		    			HashMap<Vertex, Integer> temp = new HashMap<Vertex, Integer>();
			    		temp.put(cm.get(cmKeys.get(j)), graphDist);
		    			graphDistanceCache.put(cm.get(cmKeys.get(i)), temp);
		    		}
	    		    //compute paths for graph
	    		    graphPaths = findShortestPaths(graph, cm.get(cmKeys.get(i)), cm.get(cmKeys.get(j)), graphDist);
	    		    //put into paths cache for graph
		    		if(graphPathsCache.containsKey(cm.get(cmKeys.get(i)))) {
		    			graphPathsCache.get(cm.get(cmKeys.get(i))).put(cm.get(cmKeys.get(j)), graphPaths);
		    		}
		    		else {
		    			Map<Vertex, List<List<Vertex>>> temp = new HashMap<Vertex, List<List<Vertex>>>();
			    		temp.put(cm.get(cmKeys.get(j)), graphPaths);
		    			graphPathsCache.put(cm.get(cmKeys.get(i)), temp);
		    		}
	    		}

	    		structDist += Math.abs(subgraphDist - graphDist);
	    		
	    		sumSubgraphDist += subgraphDist;
	    		sumGraphDist += graphDist;
		    }
	    }
	    if(sumSubgraphDist == 0 || sumGraphDist == 0)
			throw new RuntimeException("The sum of the structural distance: "
					+ sumSubgraphDist + " " + sumGraphDist + " is not valid. Please check.");
	    normalizedStructDist = structDist / (sumSubgraphDist + sumGraphDist);
        
	    return normalizedStructDist;
	}*/
	
	private double labelDist (Map<Vertex, Vertex> cm, DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph) {
		double totalLabelDist = 0;
	    double normalizedLabelDist = -1;
	    double sumSubgraphLabelSize = 0;
	    double sumGraphLabelSize = 0; 
	    List<Vertex> cmKeys = new ArrayList<Vertex>(cm.keySet());
	    for(int i = 0; i < cm.keySet().size() -1; i++){
	    	for(int j = i+1; j < cm.keySet().size(); j++){
	    		List<List<Vertex>> subgraphPaths = subgraphPathsCache.get(cmKeys.get(i)).get(cmKeys.get(j));
	    		List<List<Vertex>> graphPaths = graphPathsCache.get(cm.get(cmKeys.get(i))).get(cm.get(cmKeys.get(j)));

	    		List<List<String>> candidateSubgraphLabels = new ArrayList<List<String>>();
	    		for(List<Vertex> subgraphPath : subgraphPaths) { 
	    			List<List<String>> subgraphLabelSequence = new ArrayList<List<String>>();
	    		    for(int m = 0; m < subgraphPath.size()-1; m++) {
	    		    	List<String> subgraphLabels = new ArrayList<String>();
	    		    	if(!subgraph.getOutEdges(subgraphPath.get(m)).isEmpty()) {
	    		    		for(Edge edge : subgraph.getOutEdges(subgraphPath.get(m))) {
		    		    		if(edge.getDependent().equals(subgraphPath.get(m+1))){
		    		    			subgraphLabels.add(edge.getLabel());
		    		    		}
		    		    	}
	    		    	}
	    		    	if(!subgraph.getOutEdges(subgraphPath.get(m+1)).isEmpty()) {
	    		    		for(Edge edge : subgraph.getOutEdges(subgraphPath.get(m+1))) {
		    		    		if(edge.getDependent().equals(subgraphPath.get(m))){
		    		    			subgraphLabels.add(edge.getLabel());
		    		    		}
		    		    	}	
	    		    	}
	    		    	if(subgraphLabels.size() == 0)
	    		    		throw new RuntimeException("The subgraph dependency labels between : "
	    							+ subgraphPath.get(m).getToken() + " and " + subgraphPath.get(m+1).getToken() + " are not valid. Please check.");
	    		    	subgraphLabelSequence.add(subgraphLabels); 
	    		    }
	    		    
	    		    List<List<String>> intermediateSubgraphLabels = new ArrayList<List<String>>();
		    		List<List<String>> intermediateSubgraphLabelsTemp = new ArrayList<List<String>>();
		    		List<String> subgraphSequence = new ArrayList<String>();
		    		intermediateSubgraphLabels = combineLabel(subgraphLabelSequence, intermediateSubgraphLabelsTemp, subgraphSequence);

		    		candidateSubgraphLabels.addAll(intermediateSubgraphLabels);
	    		} 
	    		
	    		List<List<String>> candidateGraphLabels = new ArrayList<List<String>>();
	    		for(List<Vertex> graphPath : graphPaths) { 
	    			List<List<String>> graphLabelSequence = new ArrayList<List<String>>();
    				for(int m = 0; m < graphPath.size()-1; m++) {
    					List<String> graphLabels = new ArrayList<String>();
    					if(!graph.getOutEdges(graphPath.get(m)).isEmpty()) {
	    		    		for(Edge edge : graph.getOutEdges(graphPath.get(m))) {
		    		    		if(edge.getDependent().equals(graphPath.get(m+1))){
		    		    			graphLabels.add(edge.getLabel());
		    		    		}
		    		    	}
	    		    	}
    					if(!graph.getOutEdges(graphPath.get(m+1)).isEmpty()) {
	    		    		for(Edge edge : graph.getOutEdges(graphPath.get(m+1))) { 
	    		    			if(edge.getDependent().equals(graphPath.get(m))){
	    		    				graphLabels.add(edge.getLabel());
		    		    		}
		    		    	}	
	    		    	}
	    		    	if(graphLabels.size() == 0)
	    		    		throw new RuntimeException("The graph dependency labels between : "
	    							+ graphPath.get(m).getToken() + " and " + graphPath.get(m+1).getToken() + " are not valid. Please check.");
	    		    	graphLabelSequence.add(graphLabels); 
	    		    }
    				
    				List<List<String>> intermediateGraphLabels = new ArrayList<List<String>>();
    	    		List<List<String>> intermediateGraphLabelsTemp = new ArrayList<List<String>>();
    	    		List<String> graphSequence = new ArrayList<String>();
    	    		intermediateGraphLabels = combineLabel(graphLabelSequence, intermediateGraphLabelsTemp, graphSequence);

    	    		candidateGraphLabels.addAll(intermediateGraphLabels);
	    		}		
	    			
	    		double min = -1;
	    		double subgraphLabelSize = 0;
	    		double graphLabelSize = 0;
	    		
	    		for(List<String> subgraphLabel : candidateSubgraphLabels) { 
	    			for(List<String> graphLabel : candidateGraphLabels) {
	    			    List<String> tempSubgraphLabel= new LinkedList<String>(subgraphLabel);
	    				List<String> tempGraphLabel= new LinkedList<String>(graphLabel);
	    				int labelDist = diffList(tempSubgraphLabel, tempGraphLabel); 
	    				if(min == -1 || labelDist <= min) {
	    				    min = labelDist;
	    				    subgraphLabelSize = subgraphLabel.size(); 
    					    graphLabelSize = graphLabel.size();
	    				}
	    			}
	    		}
	    		
	    		totalLabelDist += min;
	    		
	    		sumSubgraphLabelSize += subgraphLabelSize;
	    		sumGraphLabelSize += graphLabelSize;
		    }
	    }
	    if(sumSubgraphLabelSize == 0 || sumGraphLabelSize == 0) {
	    	normalizedLabelDist = 0;
			//throw new RuntimeException("The sum of the label size: "
			//		+ sumSubgraphLabelSize + " " + sumGraphLabelSize + " is not valid. Please check.");
	    }	
	    else 
	        normalizedLabelDist = totalLabelDist / (sumSubgraphLabelSize + sumGraphLabelSize);
	    
	    return normalizedLabelDist;
	}
	
	private static List<List<String>> combineLabel (List<List<String>> matches, List<List<String>> candidateMatchings, List<String> sequence ){
		if(matches.isEmpty()){
	    	candidateMatchings.add(sequence); 
	    }
	    else {
	        List<String> n = matches.remove(0);
	        for(String i : n){
	        	List<String> s = new ArrayList<String>(sequence);
	        	s.add(i); 
	        	List<List<String>> m = new LinkedList<List<String>>(matches);
	        	candidateMatchings = combineLabel(m, candidateMatchings, s);
	        }
	    }
		return candidateMatchings;
	}
	
	/**
	 * compute difference count between two lists
	 * 
	 */
	private static int diffList(List<String> subgraphLabel, List<String> graphLabel) {
		List<String> copy = new ArrayList<String>(graphLabel);
    	for(String label : subgraphLabel){
    		if(graphLabel.contains(label)) {
    			graphLabel.remove(label);
    		}
    	}
    	for(String label : copy){
    		if(subgraphLabel.contains(label)) {
    			subgraphLabel.remove(label);
    		}
    	}
    	copy.clear();
    	
    	copy.addAll(subgraphLabel); 
    	copy.addAll(graphLabel);
    	return copy.size();// - difference;
	}
	
	private double directionalityDist (Map<Vertex, Vertex> cm, DirectedGraph<Vertex, Edge> subgraph, DirectedGraph<Vertex, Edge> graph) {
		double totalDirectionalityDist = 0;
	    double normalizedDirectionalityDist = -1;
	    double sumSubgraphDirectionalitySize = 0;
	    double sumGraphDirectionalitySize = 0; 
	    List<Vertex> cmKeys = new ArrayList<Vertex>(cm.keySet());

	    for(int i = 0; i < cm.keySet().size() - 1; i++){
	    	for(int j = i+1; j < cm.keySet().size(); j++){
	    		List<List<Vertex>> subgraphPaths = subgraphPathsCache.get(cmKeys.get(i)).get(cmKeys.get(j));
	    		List<List<Vertex>> graphPaths = graphPathsCache.get(cm.get(cmKeys.get(i))).get(cm.get(cmKeys.get(j)));
                
	    		List<List<String>> candidateSubgraphDirectionalities = new ArrayList<List<String>>();
	    		for(List<Vertex> subgraphPath : subgraphPaths) {
	    			List<List<String>> subgraphDirectionalitySequence = new ArrayList<List<String>>();
	    		    for(int m = 0; m < subgraphPath.size()-1; m++) {
	    		    	List<String> subgraphDirectionalities = new ArrayList<String>();
	    		    	if(!subgraph.getOutEdges(subgraphPath.get(m)).isEmpty()) {
	    		    		for(Edge edge : subgraph.getOutEdges(subgraphPath.get(m))) {
		    		    		if(edge.getDependent().equals(subgraphPath.get(m+1))){
		    		    			subgraphDirectionalities.add("positive");
		    		    		}
		    		    	}
	    		    	}
	    		    	if(!subgraph.getOutEdges(subgraphPath.get(m+1)).isEmpty()) {
	    		    		for(Edge edge : subgraph.getOutEdges(subgraphPath.get(m+1))) {
		    		    		if(edge.getDependent().equals(subgraphPath.get(m))){
		    		    			subgraphDirectionalities.add("negative");
		    		    		}
		    		    	}	
	    		    	}
	    		    	if(subgraphDirectionalities.size() == 0)
	    		    		throw new RuntimeException("The subgraph directionality size between : "
	    							+ subgraphPath.get(m).getToken() + " and " + subgraphPath.get(m+1).getToken() + " are not valid. Please check.");
	    		    	subgraphDirectionalitySequence.add(subgraphDirectionalities); 
	    		    }
	    		    
	    		    List<List<String>> intermediateSubgraphDirectionalities = new ArrayList<List<String>>();
		    		List<List<String>> intermediateSubgraphDirectionalitiesTemp = new ArrayList<List<String>>();
		    		List<String> subgraphSequence = new ArrayList<String>();
		    		intermediateSubgraphDirectionalities = combineLabel(subgraphDirectionalitySequence, intermediateSubgraphDirectionalitiesTemp, subgraphSequence);
		    		
		    		candidateSubgraphDirectionalities.addAll(intermediateSubgraphDirectionalities);
	    		} 
	    		
	    		
	    		List<List<String>> candidateGraphDirectionalities = new ArrayList<List<String>>();
	    		for(List<Vertex> graphPath : graphPaths) {
	    			List<List<String>> graphDirectionalitySequence = new ArrayList<List<String>>();
	    		    for(int m = 0; m < graphPath.size()-1; m++) {
	    		    	List<String> graphDirectionalities = new ArrayList<String>();
	    		    	if(!graph.getOutEdges(graphPath.get(m)).isEmpty()) {
	    		    		for(Edge edge : graph.getOutEdges(graphPath.get(m))) {
	    		    			if(edge.getDependent().equals(graphPath.get(m+1))){
	    		    				graphDirectionalities.add("positive");
		    		    		}
		    		    	}
	    		    	}
	    		    	if(!graph.getOutEdges(graphPath.get(m+1)).isEmpty()) {
	    		    		for(Edge edge : graph.getOutEdges(graphPath.get(m+1))) {
		    		    		if(edge.getDependent().equals(graphPath.get(m))){
		    		    			graphDirectionalities.add("negative");
		    		    		}
		    		    	}	
	    		    	}
	    		    	if(graphDirectionalities.size() == 0)
	    		    		throw new RuntimeException("The graph directionality size between : "
	    							+ graphPath.get(m).getToken() + " and " + graphPath.get(m+1).getToken() + " are not valid. Please check.");
	    		    	
	    		    	graphDirectionalitySequence.add(graphDirectionalities); 
	    		    }
	    		    
	    		    List<List<String>> intermediateGraphDirectionalities = new ArrayList<List<String>>();
		    		List<List<String>> intermediateGraphDirectionalitiesTemp = new ArrayList<List<String>>();
		    		List<String> graphSequence = new ArrayList<String>();
		    		intermediateGraphDirectionalities = combineLabel(graphDirectionalitySequence, intermediateGraphDirectionalitiesTemp, graphSequence);
	    		    
		    		candidateGraphDirectionalities.addAll(intermediateGraphDirectionalities);
	    		} 
	    			
	    		double min = -1;
	    		double subgraphDirectionalitySize = 0;
	    		double graphDirectionalitySize = 0;
	    		
	    		for(List<String> subgraphDirectionality : candidateSubgraphDirectionalities) {
	    			for(List<String> graphDirectionality : candidateGraphDirectionalities) {
	    				List<String> tempSubgraphDirectionality= new LinkedList<String>(subgraphDirectionality);
	    				List<String> tempGraphDirectionality= new LinkedList<String>(graphDirectionality);
	    				int directionalityDist = diffList(tempSubgraphDirectionality, tempGraphDirectionality);	
	    				if(min == -1 || directionalityDist <= min) {
	    				    min = directionalityDist;
	    				    subgraphDirectionalitySize = subgraphDirectionality.size(); 
	    					graphDirectionalitySize = graphDirectionality.size(); 
	    				}
	    			}
	    		}

	    		totalDirectionalityDist += min;
	    		
	    		sumSubgraphDirectionalitySize += subgraphDirectionalitySize;
	    		sumGraphDirectionalitySize += graphDirectionalitySize;
		    }
	    }
	    if(sumSubgraphDirectionalitySize == 0 || sumGraphDirectionalitySize == 0) {
	    	normalizedDirectionalityDist = 0;
	    	//throw new RuntimeException("The sum of the directionality size: "
			//		+ sumSubgraphDirectionalitySize + " " + sumGraphDirectionalitySize + " is not valid. Please check.");
	    }	
	    else 
	        normalizedDirectionalityDist = totalDirectionalityDist / (sumSubgraphDirectionalitySize + sumGraphDirectionalitySize);
	    
	    return normalizedDirectionalityDist;
	}
	
	/**
	 * Calculate shortest distance between two nodes in a graph using Dijkstra's algorithm
	 * @param graph : input graph
	 * @param source : source node
	 * @param target : target node
	 * @return shortest distance in integer
	 */
	public static int shortestDistance (DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target){
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
	public static List<List<Vertex>> findShortestPaths (DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target, int shortestDistance){
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
	public static List<List<Vertex>> findAllPaths(DirectedGraph<Vertex, Edge> graph, Vertex source, Vertex target) {
		List<List<Vertex>> paths = new ArrayList<List<Vertex>>();
		List<Vertex> visited = new ArrayList<Vertex>();
		visited.add(source); 
		paths = findAllPaths(graph, visited, paths, source, target); 
		return paths;
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
	
	private void computeSubgraphPairwiseShortestDistanceAndPaths(DirectedGraph<Vertex, Edge> subgraph) {
    	List<Vertex> nodes = new ArrayList<Vertex>(subgraph.getVertices());
    	
    	for(int i = 0; i < nodes.size() - 1; i++){
	    	for(int j = i+1; j < nodes.size(); j++){ 
	    		//compute distance for subgraph
    		    int subgraphDist = shortestDistance(subgraph, nodes.get(i), nodes.get(j));
    		    
    		    //put into distance cache for subgraph
    		    if(subgraphDistanceCache.containsKey(nodes.get(i))) {
	    			subgraphDistanceCache.get(nodes.get(i)).put(nodes.get(j), subgraphDist);
	    		}
	    		else {
	    			HashMap<Vertex, Integer> temp = new HashMap<Vertex, Integer>();
		    		temp.put(nodes.get(j), subgraphDist);
	    			subgraphDistanceCache.put(nodes.get(i), temp);
	    		}
    		    //reverse direction
    		    if(subgraphDistanceCache.containsKey(nodes.get(j))) {
	    			subgraphDistanceCache.get(nodes.get(j)).put(nodes.get(i), subgraphDist);
	    		}
	    		else {
	    			HashMap<Vertex, Integer> temp = new HashMap<Vertex, Integer>();
		    		temp.put(nodes.get(i), subgraphDist);
	    			subgraphDistanceCache.put(nodes.get(j), temp);
	    		}
    		    
    		    //compute paths for subgraph
    		    List<List<Vertex>> subgraphPaths = findShortestPaths(subgraph, nodes.get(i), nodes.get(j), subgraphDist);
    		    List<List<Vertex>> reverseSubgraphPaths = findShortestPaths(subgraph, nodes.get(j), nodes.get(i), subgraphDist);

    		    //put into paths cache for subgraph
    		    if(subgraphPathsCache.containsKey(nodes.get(i))) {
    		    	subgraphPathsCache.get(nodes.get(i)).put(nodes.get(j), subgraphPaths);
	    		}
	    		else {
	    			Map<Vertex, List<List<Vertex>>> temp = new HashMap<Vertex, List<List<Vertex>>>();
		    		temp.put(nodes.get(j), subgraphPaths);
	    			subgraphPathsCache.put(nodes.get(i), temp);
	    		}
    		    //reverse direction
    		    if(subgraphPathsCache.containsKey(nodes.get(j))) {
	    			subgraphPathsCache.get(nodes.get(j)).put(nodes.get(i), reverseSubgraphPaths);
	    		}
	    		else {
	    			Map<Vertex, List<List<Vertex>>> temp = new HashMap<Vertex, List<List<Vertex>>>();
		    		temp.put(nodes.get(i), reverseSubgraphPaths);
	    			subgraphPathsCache.put(nodes.get(j), temp);
	    		}
	    	}
    	}
    }
}





