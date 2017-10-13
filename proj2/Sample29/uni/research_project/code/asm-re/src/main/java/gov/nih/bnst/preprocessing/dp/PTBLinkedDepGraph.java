package gov.nih.bnst.preprocessing.dp;


import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


import edu.ucdenver.ccp.nlp.biolemmatizer.BioLemmatizer;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import gov.nih.bnst.preprocessing.pt.PennTree;
import gov.nih.bnst.preprocessing.pt.Token;

/**
 * wrapper class for the directed graph defined in JUNG package
 * @author liuh11
 *
 */
public class PTBLinkedDepGraph implements DependencyGraph {
	/**
	 * Constructor to create graphs from dependency representation
	 * @param r : input dependency representation separated by ";"
	 * @return created dependency graph
	 */
	public PTBLinkedDepGraph(String r, PennTree tree) {
		//Initialize class fields
		graph = new DirectedSparseGraph<Vertex,Edge>();
		tokenToNode = new HashMap<String, Vertex>();
		dependencyParses = new HashSet<String>();

		//Retrieve mapping info from tree
		Map<String, Token> treeTokenMap = tree.getTokenMap();

		/** dr: a single dependency representation */
		for ( String dr : r.split("\\s*\\t\\s*") ) {
			//ignore dependency parse involving ROOT-0 to be consistent with penntree bank tree
			if( dr.indexOf("root(ROOT-0") != -1 ) continue;
			//recording original dependency parse
			dependencyParses.add(dr);
			if ( ! dr.matches("^\\S+\\(\\S+\\s*,\\s*\\S+\\)\\s*$") )
		    	throw new RuntimeException("The dependency representation: "
						+ dr + " is not valid. Please check.");
		    Matcher md = Pattern.compile("^(\\S+?)\\((\\S+?)\\x27*\\s*,\\s*(\\S+?)\\x27*\\)\\s*$").matcher(dr);
		    md.find();
		    String label = md.group(1);
		    String g = md.group(2);
		    String d = md.group(3);

		    Vertex gov; //System.out.println(treeTokenMap.keySet());
		    if(!tokenToNode.containsKey(g)) {
		        //do not insert to the graph if the token is not valid
		    	if(treeTokenMap.get(g) == null)
		        	continue;
		    	gov = new Vertex(g); //System.out.println(g);
		        //link tree token to graph node
		        gov.setTreeToken(treeTokenMap.get(g));
		        gov.setPOStag(treeTokenMap.get(g).getPOSTag());
		        gov.setOffset(treeTokenMap.get(g).getOffset());
		        //link graph node to tree token
		        treeTokenMap.get(g).setGraphNode(gov);
		        graph.addVertex(gov);
		        tokenToNode.put(g, gov);
		    }
		    else { gov = tokenToNode.get(g); }

		    Vertex dep;
		    if(!tokenToNode.containsKey(d)) {
		    	//do not insert to the graph if the token is not valid
		    	if(treeTokenMap.get(d) == null)
		        	continue;
		    	dep = new Vertex(d);
		        //link tree token to graph node
		        dep.setTreeToken(treeTokenMap.get(d));
		        dep.setPOStag(treeTokenMap.get(d).getPOSTag());
		        dep.setOffset(treeTokenMap.get(d).getOffset());
		        //link graph node to tree token
		        treeTokenMap.get(d).setGraphNode(dep);
		        graph.addVertex(dep);
		        tokenToNode.put(d, dep);
		    }
		    else { dep = tokenToNode.get(d); }

		    Edge govToDep = new Edge(gov, label, dep);
		    graph.addEdge(govToDep, gov, dep);
		}

		/** generates lemma for each node */
		generateLemmas(graph.getVertices());
    }
	/** dependency graph to be built */
	protected DirectedGraph<Vertex,Edge> graph;
	/** mapping between token string to corresponding node in graph */
	protected Map<String, Vertex> tokenToNode;
	/** all dependency parses that constitute the graph*/
	protected Set<String> dependencyParses;
	/** a set of start nodes of graph, whose token occurs in Semcat category */
	private Set<Vertex> startNodes;
	/** load BioLemmatizer */
	private static BioLemmatizer bioLemmatizer = new BioLemmatizer();

	/**
	 * Generate lemma and generalized POS tag for each node in the graph
	 * and set the correponding fields in the nodes for the node comparison process
	 * @param nodes : nodes for which the lemma and generalized POS will be generated
	 */
	protected static void generateLemmas(Collection<Vertex> nodes) {
	    try {
	    	for(Vertex node : nodes) {
				String lemma = node.getWord();
				lemma = lemma.replaceAll("-", "");
				if(lemma.matches("^BIO_Entity.*$")) {
					lemma = "BIO_Entity";
				}
				else lemma = bioLemmatizer.lemmatizeByLexiconAndRules(lemma, node.getPOSTag()).lemmasToString();
				//lemma = lemma.replaceAll("\\d", "");
				node.setLemma(lemma.toLowerCase());
				//set lemma for the corresponding token of the node as well
				node.getTreeToken().setLemma(lemma.toLowerCase());

				String tag = node.getPOSTag();
                String[] nounTags = {"NNS", "NNP", "NNPS", "NN"};
				String[] adjectiveTags = {"JJR", "JJS", "JJ"};
				String[] adverbTags = {"RBR", "RBS", "RB"};
				String[] verbTags = {"VBD", "VBP", "VBZ", "VB", "VBG", "VBN"};
                if(Arrays.asList(nounTags).contains(tag))
					tag = "NN";
				else if(Arrays.asList(adjectiveTags).contains(tag))
					tag = "JJ";
				else if(Arrays.asList(adverbTags).contains(tag))
					tag = "RB";
				else if(Arrays.asList(verbTags).contains(tag))
				    tag = "VB";

				//set compare form
				node.setCompareForm( (lemma + " " + tag).toLowerCase() );
				node.setGeneralizedPOS(tag);
				//set compare form for the corresponding token of the node as well
				node.getTreeToken().setCompareForm( (lemma + " " + tag).toLowerCase() );
			}
	    } catch (Exception e) {
			e.printStackTrace();
	    }
	}

	/**
	 * set the startNodes of the graph
	 */
	public void setStartNodes(Set<Vertex> startNodes) {
		this.startNodes = startNodes;
	}

	/**
	 * retrieve the startNodes of the graph
	 */
	public Set<Vertex> getStartNodes() {
		return startNodes;
	}

	/**
	 * retrieve the token-to-node mapping of the graph
	 * @return token-to-node mapping
	 */
	public Map<String, Vertex> getTokenToNodeMapping() {
		return tokenToNode;
	}

	/**
	 * retrieve the node of the graph using its token
	 * @return node of the graph
	 */
	@Override
	public Vertex getNodeFromToken(String token) {
		return tokenToNode.get(token);
	}

	/**
	 * retrieve the dependency graph defined in JUNG package
	 * @return graph
	 */
	@Override
	public DirectedGraph<Vertex,Edge> getGraph() {
		return graph;
	}

}
