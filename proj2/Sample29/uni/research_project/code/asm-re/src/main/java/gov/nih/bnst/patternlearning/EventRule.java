package gov.nih.bnst.patternlearning;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;
import edu.ucdenver.ccp.nlp.biolemmatizer.BioLemmatizer;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import gov.nih.bnst.preprocessing.annotation.Event;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.combine.training.CombineInfo;
import gov.nih.bnst.eventextraction.ASM;

/**
 * class to store detailed info about individual dependency path
 *
 */
public class EventRule {
	private static final Logger LOG = LoggerFactory.getLogger(EventRule.class);

	/** the stored path (directed graph) */
	private DirectedGraph<Vertex, Edge> path;
	/** corresponding PMID */
	private String pmid;
	/** corresponding sentence ID */
	private int sentenceID;
	/** event rule ID */
	private String ruleID;
	/** sign to determine this path should be removed or not in the later process */
	private boolean removalSign;
	/** gold event */
	private Event goldEvent;
	/** trigger nodes */
	private Set<Vertex> triggers;
	/** theme nodes */
	private Set<Vertex> themes;
	/** cause node */
	private Vertex cause = null;
	/** event rule category */
	private String category;
	/** event node of the theme */
	private Vertex themeEvent = null;
	/** theme event category */
	private String themeEventCategory;
	/** determine if cause is an event */
	private Vertex causeEvent = null;
	/** cause event category */
	private String causeEventCategory;
	/** event rule type (for cause rules only) */
	private String ruleType;
	/** original event rule string, for testing data */
	private String eventRuleString;
	/** pairwise shortest distance cache of the rule */
	private Map<Vertex, Map<Vertex, Integer>> distanceCache;
    /** pairwise shortest paths cache of the rule */
	private Map<Vertex, Map<Vertex, List<List<Vertex>>>> pathsCache;
	/** load BioLemmatizer */
	private static BioLemmatizer bioLemmatizer = new BioLemmatizer();

	/**
	 * Constructor to initalize some class fields
	 * @param path : the directed graph to be stored
	 */
	public EventRule (DirectedGraph<Vertex, Edge> path, Event goldEvent, AnnotatedSentence sentence, String pmid){
		this.pmid = pmid;
		this.path = path;
		removalSign = false;
		sentenceID = sentence.getSentenceID();
		this.goldEvent = goldEvent;
		category = goldEvent.getEventCategory();
		triggers = new HashSet<Vertex>();
		themes = new HashSet<Vertex>();
		//theme
		for(String theme : goldEvent.getEventThemes()) {
			if(theme.charAt(0) == 'T') {
                //Themes are either proteins, in the case of
                //Genia, or arguments, in the case of Variome
                //and SeeDev. If neither, emit a warning.
                Vertex themeVertex;
                if (sentence.getProteins() != null){
                    themeVertex = sentence.getProteins().get(theme).getGraphNode();
                }
                else if (sentence.getArguments() != null) {
                    themeVertex = sentence.getArguments().get(theme).getGraphNode();
                }
                else {
                    LOG.warn(
                        "No vertices found for theme {}"
                        + "in event {} for sentence {}",
                        theme, goldEvent.getEventID(), sentence.getSentenceID()
                    );
                    continue;
                }
                themes.add(themeVertex);
			}
			else if(theme.charAt(0) == 'E') {
				themeEventCategory = sentence.getEvents().get(theme).getEventCategory();
				String trigger = sentence.getEvents().get(theme).getEventTrigger();
			    themeEvent = sentence.getTriggers().get(trigger).getTriggerCenterNode();
			}
		}
		//cause
		if(goldEvent.hasCause()) {
			if(goldEvent.getEventCause().charAt(0) == 'T') {
				cause = sentence.getProteins().get(goldEvent.getEventCause()).getGraphNode();
			}
			else if(goldEvent.getEventCause().charAt(0) == 'E') {
				causeEventCategory = sentence.getEvents().get(goldEvent.getEventCause()).getEventCategory();
				String trigger = sentence.getEvents().get(goldEvent.getEventCause()).getEventTrigger();
			    causeEvent = sentence.getTriggers().get(trigger).getTriggerCenterNode();
			}
		}
		//trigger
        if (goldEvent.getEventTrigger() != null) {
            for(Vertex v : sentence.getTriggers().get(goldEvent.getEventTrigger()).getTriggerNodes())
    			triggers.add(v);
        }
	}

	/**
	 * Constructor to initalize some class fields
	 * @param path : the directed graph to be stored
	 */
	public EventRule (DirectedGraph<Vertex, Edge> path, Event goldEvent, AnnotatedSentence sentence, String pmid, String ruleType){
		LOG.trace("Creating {} rule for graph {}, event {}, Doc ID {}", ruleType, path, goldEvent, pmid);
		this.pmid = pmid;
		this.path = path;
		removalSign = false;
		sentenceID = sentence.getSentenceID();
		this.goldEvent = goldEvent;
		category = goldEvent.getEventCategory();
		triggers = new HashSet<Vertex>();
		themes = new HashSet<Vertex>();
		this.ruleType = ruleType;
		//theme
		if(ruleType.equals("Theme")) {
			for(String theme : goldEvent.getEventThemes()) {
				if(theme.charAt(0) == 'T') {
				    Vertex v = sentence.getProteins().get(theme).getGraphNode();
				    themes.add(v);
				}
				else if(theme.charAt(0) == 'E') {
					themeEventCategory = sentence.getEvents().get(theme).getEventCategory();
					String trigger = sentence.getEvents().get(theme).getEventTrigger();
				    themeEvent = sentence.getTriggers().get(trigger).getTriggerCenterNode();
				}
			}
		}
		//cause
		else if(ruleType.equals("Cause")) {
			if(goldEvent.getEventCause().charAt(0) == 'T') {
				cause = sentence.getProteins().get(goldEvent.getEventCause()).getGraphNode();
			}
			else if(goldEvent.getEventCause().charAt(0) == 'E') {
				causeEventCategory = sentence.getEvents().get(goldEvent.getEventCause()).getEventCategory();
				String trigger = sentence.getEvents().get(goldEvent.getEventCause()).getEventTrigger();
			    causeEvent = sentence.getTriggers().get(trigger).getTriggerCenterNode();
			}
		}
		//trigger
		for(Vertex v : sentence.getTriggers().get(goldEvent.getEventTrigger()).getTriggerNodes())
			triggers.add(v);
	}

	/**
	 * constructor for reading rules from generated rule string
	 * @param eventRuleString
	 */
	public EventRule(String eventRuleString, String category) {
		//initialize
		triggers = new HashSet<Vertex>();
		themes = new HashSet<Vertex>();
		distanceCache = new HashMap<Vertex, Map<Vertex, Integer>>();
		pathsCache = new HashMap<Vertex, Map<Vertex, List<List<Vertex>>>>();
		this.removalSign = false;
		this.eventRuleString = eventRuleString;
        this.category = category;

        LOG.info("Reading rule {}", eventRuleString);
        /** record the rule ID */
		Matcher m = Pattern.compile("^(\\d+):\\t([^\\t]*)(\\t(.+)\\t(.+)\\t(.+))?$").matcher(eventRuleString);

		if(!m.find())
			throw new RuleParsingException("The event rule: "
					+ eventRuleString + " is not valid. Please check.");
		this.ruleID = m.group(1);
        LOG.info("Read rule ID {}", ruleID);

		/** analyze lhs (left hand side) and rhs (right hand side) of the rule */
		String[] r = m.group(2).split("\\s*<==\\s*");
        LOG.info("Left hand side: {}", r[0]);
        LOG.info("Right hand side (dependency graph): {}", r[1]);

		//Initialize class fields
		path = new DirectedSparseGraph<Vertex,Edge>();
		//mapping between token string to corresponding node in graph
		Map<String, Vertex> tokenToNode = new HashMap<String, Vertex>();
		//right hand side: generate graph
		/** dr: a single dependency representation */
		for ( String dr : r[1].split("; ") ) {
            LOG.info("Processing dependency representation: {}", dr);
            if ( ! dr.matches("^\\S+\\(\\S+\\s*,\\s*\\S+\\)\\s*$") )
		    	throw new RuleParsingException("The dependency representation: "
						+ dr + " is not valid. Please check.");
		    Matcher md = Pattern.compile("^(\\S+?)\\((\\S+?)\\x27*\\s*,\\s*(\\S+?)\\x27*\\)\\s*$").matcher(dr);
		    md.find();
		    String label = md.group(1);
		    String g = md.group(2);
		    String d = md.group(3);

            LOG.info("Category: {}", label);
            LOG.info("Govering: {}", g);
            LOG.info("Dependent: {}", d);

		    Vertex gov;
		    if(!tokenToNode.containsKey(g)) {
		    	gov = new Vertex(g, "test");
		        path.addVertex(gov);
		        tokenToNode.put(g, gov);
		    }
		    else { gov = tokenToNode.get(g); }

		    Vertex dep;
		    if(!tokenToNode.containsKey(d)) {
		    	dep = new Vertex(d, "test");
		        path.addVertex(dep);
		        tokenToNode.put(d, dep);
		    }
		    else { dep = tokenToNode.get(d); }

		    Edge govToDep = new Edge(gov, label, dep);
		    path.addEdge(govToDep, gov, dep);
		}

        LOG.info("Created token -> node map: {}", tokenToNode);
        LOG.info("Parsed dependency path: {}", path);

		/** generates lemma for each node */
		generateLemmas(path.getVertices());

		/** computes pairwise shortest distance and paths of the rule */
		computeSubgraphPairwiseShortestDistanceAndPaths(path);

		//left hand side
		/** record the trigger and argument nodes of the rule */
		Matcher n = Pattern.compile("(\\w+?:\\(.+?\\))").matcher(r[0]);
        LOG.info("Parsing left hand side: {}", r[0]);
        while(n.find()) {
			String argument = n.group();
			Matcher t = Pattern.compile("^(\\w+):\\((.+)\\)$").matcher(argument);
			if(!t.find())
				throw new RuleParsingException("The component of rule: "
						+ argument + " is not valid. Please check.");
			String title = t.group(1);
			String content = t.group(2);

            LOG.info("Rule title: {}", title);
            LOG.info("Rule content: {}", content);

			if(title.equals(category)) {
				String[] triggers = content.split("\\s+");
				for(String trigger : triggers){
                    LOG.info("Processing trigger {}", trigger);
                    Vertex node = tokenToNode.get(trigger);
                    //TODO: We now have event rules without triggers, and therefore
                    //need to process them correctly.
                    if(node == null) {
                        //throw new RuleParsingException("there is no such node in the graph " + trigger);
					    continue;
					}
					node.setIsTrigger(true);
					this.triggers.add(node);
				}
			}
			else if(title.matches("Theme\\d*")) {
				Matcher p = Pattern.compile("^(.+):.+$").matcher(content);
				if(p.find()) {
					themeEventCategory = p.group(1);
					content = content.replaceAll("^.+:", "");
					Vertex node = tokenToNode.get(content);
					if(node == null) {
						throw new RuleParsingException("there is no such node in the graph " + content);
					}
					themeEvent = node;
					themes.add(node);
				}
				else {
					Vertex node = tokenToNode.get(content);
					if(node == null) {
						throw new RuleParsingException("there is no such node in the graph " + content);
					}
					node.setIsProtein(true);
					themes.add(node);
				}
			}
			else if(title.equals("Cause")) {
				Matcher p = Pattern.compile("^(.+):.+$").matcher(content);
				if(p.find()) {
					causeEventCategory = p.group(1);
					content = content.replaceAll("^.+:", "");
					Vertex node = tokenToNode.get(content);
					if(node == null) {
						throw new RuleParsingException("there is no such node in the graph " + content);
					}
					causeEvent = node;
					cause = node;
				}
				else {
					Vertex node = tokenToNode.get(content);
					if(node == null) {
						throw new RuleParsingException("there is no such node in the graph " + content);
					}
					node.setIsProtein(true);
					cause = node;
				}
			}
		}
		if(!hasTheme()) ruleType = "Cause";
	}

	/**
	 * Generate lemma and generalized POS tag for each node in the graph
	 * and set the correponding fields in the nodes for the node comparison process
	 * @param nodes : nodes for which the lemma and generalized POS will be generated
	 */
	private static void generateLemmas(Collection<Vertex> nodes) {
	    try {
	    	for(Vertex node : nodes) {
	    		//deal separately with artificially split graph nodes such as "-dependent-30/"
	    		if(node.getPOSTag().isEmpty()) {
	    			//set compare form
					node.setCompareForm( node.getWord().toLowerCase() );
					node.setGeneralizedPOS(node.getPOSTag());
					continue;
	    		}
				String lemma = node.getWord();
				lemma = lemma.replaceAll("-", "");
				if(lemma.matches("(?i)^BIO_Entity\\d*$")) {
					lemma = "BIO_Entity";
				}
				else {
					try {
					lemma = bioLemmatizer.lemmatizeByLexiconAndRules(lemma, node.getPOSTag()).lemmasToString();
					} catch (Exception e) {
						LOG.error("Error while lemmatizing {}; falling back to unmodified form; full trace shown below", lemma);
						e.printStackTrace();
					}
				}
				//lemma = lemma.replaceAll("\\d", "");
				node.setLemma(lemma.toLowerCase());

				String[] nounTags = {"NNS", "NNP", "NNPS", "NN"};
				String[] adjectiveTags = {"JJR", "JJS", "JJ"};
				String[] adverbTags = {"RBR", "RBS", "RB"};
				String[] verbTags = {"VBD", "VBP", "VBZ", "VB", "VBG", "VBN"};

				String tag = node.getPOSTag();
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
			}
	    } catch (Exception e) {
			e.printStackTrace();
	    }
	}

	private void computeSubgraphPairwiseShortestDistanceAndPaths(DirectedGraph<Vertex, Edge> subgraph) {
    	List<Vertex> nodes = new ArrayList<Vertex>(subgraph.getVertices());

    	for(int i = 0; i < nodes.size() - 1; i++){
	    	for(int j = i+1; j < nodes.size(); j++){
	    		//compute distance for subgraph
    		    int subgraphDist = ASM.shortestDistance(subgraph, nodes.get(i), nodes.get(j));

    		    //put into distance cache for subgraph
    		    if(distanceCache.containsKey(nodes.get(i))) {
	    			distanceCache.get(nodes.get(i)).put(nodes.get(j), subgraphDist);
	    		}
	    		else {
	    			HashMap<Vertex, Integer> temp = new HashMap<Vertex, Integer>();
		    		temp.put(nodes.get(j), subgraphDist);
	    			distanceCache.put(nodes.get(i), temp);
	    		}
    		    //reverse direction
    		    if(distanceCache.containsKey(nodes.get(j))) {
	    			distanceCache.get(nodes.get(j)).put(nodes.get(i), subgraphDist);
	    		}
	    		else {
	    			HashMap<Vertex, Integer> temp = new HashMap<Vertex, Integer>();
		    		temp.put(nodes.get(i), subgraphDist);
	    			distanceCache.put(nodes.get(j), temp);
	    		}

    		    //compute paths for subgraph
    		    List<List<Vertex>> subgraphPaths = ASM.findShortestPaths(subgraph, nodes.get(i), nodes.get(j), subgraphDist);
    		    List<List<Vertex>> reverseSubgraphPaths = ASM.findShortestPaths(subgraph, nodes.get(j), nodes.get(i), subgraphDist);

    		    //put into paths cache for subgraph
    		    if(pathsCache.containsKey(nodes.get(i))) {
    		    	pathsCache.get(nodes.get(i)).put(nodes.get(j), subgraphPaths);
	    		}
	    		else {
	    			Map<Vertex, List<List<Vertex>>> temp = new HashMap<Vertex, List<List<Vertex>>>();
		    		temp.put(nodes.get(j), subgraphPaths);
	    			pathsCache.put(nodes.get(i), temp);
	    		}
    		    //reverse direction
    		    if(pathsCache.containsKey(nodes.get(j))) {
	    			pathsCache.get(nodes.get(j)).put(nodes.get(i), reverseSubgraphPaths);
	    		}
	    		else {
	    			Map<Vertex, List<List<Vertex>>> temp = new HashMap<Vertex, List<List<Vertex>>>();
		    		temp.put(nodes.get(i), reverseSubgraphPaths);
	    			pathsCache.put(nodes.get(j), temp);
	    		}
	    	}
    	}
    }

	/**
     * print event rule content
     * Example: Positive_regulation:(Induction-1/NN) Theme:(Negative_regulation:inhibits-2/VBZ) <== dep(inhibits-2/VBZ, Induction-1/NN)
     */
    @Override
	public String toString(){
    	StringBuilder sb = new StringBuilder();
    	if(ruleID != null)
    		sb.append(ruleID + ":\t");
    	sb.append(category);
		sb.append(":(");
		List<Vertex> sorted = new ArrayList<Vertex>(triggers);
		Collections.sort(sorted, new MyComparator());
		sb.append( join(sorted, " ") );
		sb.append(") ");
		if(ruleType != null && ruleType.equals("Cause")) {
			if(isCauseEvent()) {
				sb.append("Cause:(" + causeEventCategory + ":" + causeEvent + ") ");
			}
			else {
				sb.append("Cause:(" + cause + ") ");
			}
		}
		else if(ruleType != null && ruleType.equals("Theme")) {
			if(isThemeEvent()) {
				sb.append("Theme:(" + themeEventCategory + ":" + themeEvent + ") ");
			}
			else {
				List<Vertex> temp = new ArrayList<Vertex>(themes);
				sb.append("Theme:(" + temp.get(0) + ") ");
				for(int i=1; i<temp.size(); i++) {
					sb.append("Theme" + (i+1) + ":(" + temp.get(i) + ") ");
				}
			}
		}
		else {
			if(isThemeEvent()) {
				sb.append("Theme:(" + themeEventCategory + ":" + themeEvent + ") ");
			}
			else {
				List<Vertex> temp = new ArrayList<Vertex>(themes);
				sb.append("Theme:(" + temp.get(0) + ") ");
				for(int i=1; i<temp.size(); i++) {
					sb.append("Theme" + (i+1) + ":(" + temp.get(i) + ") ");
				}
			}
			if(hasCause()) {
				if(isCauseEvent()) {
					sb.append("Cause:(" + causeEventCategory + ":" + causeEvent + ") ");
				}
				else {
					sb.append("Cause:(" + cause + ") ");
				}
			}
		}
		sb.append("<== ");
		List<String> edges = new ArrayList<String>();
		for(Edge e : path.getEdges()) {
			edges.add(e.toString());
		}
		sb.append(CombineInfo.join(edges, "; "));
		return sb.toString();
    }

    /**
     * retrieve the stored dependency graph
     * @return path
     */
    public DirectedGraph<Vertex, Edge> getGraph() {
    	return path;
    }

    /**
     * set pmid of the rule
     * @param pmid
     */
    public void setPMID(String pmid) {
    	this.pmid = pmid;
    }

    /**
     * check isThemeEvent
     */
    public boolean isThemeEvent() {
    	return themeEvent != null;
    }

    public Vertex getThemeEvent() {
    	return themeEvent;
    }

    public String getThemeEventCategory() {
    	return themeEventCategory;
    }

    /**
     * check isCauseEvent
     */
    public boolean isCauseEvent() {
    	return causeEvent != null;
    }

    public Vertex getCauseEvent() {
    	return causeEvent;
    }

    public String getCauseEventCategory() {
    	return causeEventCategory;
    }

    /**
     * check if the event rule has a theme
     */
    public boolean hasTheme() {
    	return !themes.isEmpty();
    }

    /**
     * check if the event rule has a cause
     */
    public boolean hasCause() {
		return this.cause != null;
	}

    /**
     * retrieve pmid ID of the rule
     * @return pmid ID
     */
    public String getPMID() {
    	return pmid;
    }

    /**
     * set sentence id of the rule
     * @param sentenceID
     */
    public void setSentenceID(int sentenceID) {
    	this.sentenceID = sentenceID;
    }

    /**
     * retrieve sentence ID of the rule
     * @return sentence ID
     */
    public int getSentenceID() {
    	return sentenceID;
    }

    /**
     * retrieve gold event of the rule
     * @return gold event
     */
    public Event getGoldEvent() {
    	return goldEvent;
    }

    /**
     * retrieve event rule ID
     * @return event rule ID
     */
    public String getRuleID() {
    	return ruleID;
    }

    /**
     * set removal sign of the rule
     * @param removalSign
     */
    public void setRemovalSign(boolean removalSign) {
    	this.removalSign = removalSign;
    }

    /**
     * retrieve removal sign of the rule
     * @return removal sign
     */
    public boolean getRemovalSign() {
    	return removalSign;
    }

    public String getEventCategory() {
    	return category;
    }

    public String getEventRuleString() {
    	return eventRuleString;
    }

    public Set<Vertex> getEventTriggers() {
    	return triggers;
    }

    public Set<Vertex> getEventThemes() {
    	return themes;
    }

    public Vertex getEventCause() {
    	return cause;
    }

	/**
	 * retrieve pairwise shortest distance cache of the rule
	 * @return distance cache
	 */
	public Map<Vertex, Map<Vertex, Integer>> getDistanceCache() {
		return distanceCache;
	}

	/**
	 * retrieve pairwise shortest paths cache of the rule
	 * @return paths cache
	 */
	public Map<Vertex, Map<Vertex, List<List<Vertex>>>> getPathsCache() {
		return pathsCache;
	}

	public static final String join(List<Vertex> c, String delimiter) {
		if (c.isEmpty()) {
			return "";
		}
		StringBuffer buffer = new StringBuffer(c.get(0).toString());
		for(int i=1; i<c.size(); i++) {
			buffer.append(delimiter).append(c.get(i).toString());
		}
		return buffer.toString();
	}

	public void setRuleID(String ruleID) {
		this.ruleID = ruleID;
	}
}
