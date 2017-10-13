package gov.nih.bnst13.preprocessing.combine.training;

import gov.nih.bnst13.patternlearning.EventRule;
import gov.nih.bnst13.preprocessing.annotation.Event;
import gov.nih.bnst13.preprocessing.annotation.Protein;
import gov.nih.bnst13.preprocessing.annotation.Trigger;
import gov.nih.bnst13.preprocessing.dp.DependencyGraph;
import gov.nih.bnst13.preprocessing.dp.PTBLinkedDepGraph;
import gov.nih.bnst13.preprocessing.pt.PennTree;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;




/**
 * <p>Read Dstore output of each sentence and transform it into Dependency Graph object and PennTree Bank style tree object </p>
 *
 */
public class ReadSingleSentenceOutput implements AnnotatedSentence {
	/** sentence ID */
	private int sentenceID;
	/** McClosky/Stanford/whatever dependency graph */
	private DependencyGraph graph = null;
	/** penntree bank tree */
	private PennTree tree = null;
	/** the start index of the sentence */
	private final int startIndex;
	/**
	 * endIndex is the starting index of the next sentence, 
	 * so this upper bound shoud not be reached in this sentence
	 */
	private final int endIndex;
	/** proteins that belong to the sentence */
	private Map<String, Protein> proteins = null;
	/** triggers that belong to the sentence */
	private Map<String, Trigger> triggers = null;
	/** events that belong to the sentence */
	private Map<String, Event> events = null;
	/** event rules of the sentence */
	private List<EventRule> eventRulesOfSentence;
	
	/**
	 * Constructor to initialize the class fields of graph and tree 
	 * @param graph : dependency parses dstore input
	 * @param tree : penntree bank tree dstore input
	 */
	public ReadSingleSentenceOutput (int sentenceID, int endIndex, String tree, List<Integer> offset, String graph) {
		this.sentenceID = sentenceID;
		this.tree = new PennTree(tree, offset);
		//dependency graph needs tree to get the POS tagging info
		//as original dependency graph doesn't have POS info
		//dependency parses are delimited using "tab"
		this.graph = new PTBLinkedDepGraph(graph, this.tree);	
		startIndex = offset.get(0);
		this.endIndex = endIndex;
		if(endIndex != -1 && startIndex >= endIndex)
			throw new RuntimeException("start index " + startIndex + " cannot be bigger than end index " + endIndex);
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getDependencyGraph(java.lang.String)
	 */
	@Override
	public DependencyGraph getDependencyGraph() {
		return graph;
	}
	
	/**
	 * retrieve the penntree bank tree
	 * @return penntree bank tree
	 */
	public PennTree getPennTree() {
		return tree;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getSentenceID()
	 */
	@Override
	public int getSentenceID() {
		return sentenceID;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getStartIndex()
	 */
	@Override
	public int getStartIndex() {
		return startIndex;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getEndIndex()
	 */
	@Override
	public int getEndIndex() {
		return endIndex;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getEventRulesOfSentence()
	 */
	@Override
	public List<EventRule> getEventRulesOfSentence() {
		return eventRulesOfSentence;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#setEventRulesOfSentence(java.util.List)
	 */
	@Override
	public void setEventRulesOfSentence(List<EventRule> eventRulesOfSentence) {
		this.eventRulesOfSentence = eventRulesOfSentence;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#setProteins(java.util.Map)
	 */
	@Override
	public void setProteins(Map<String, Protein> proteins) {
		this.proteins = proteins;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getProteins()
	 */
	@Override
	public Map<String, Protein> getProteins() {
		return proteins;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#setTriggers(java.util.Map)
	 */
	@Override
	public void setTriggers(Map<String, Trigger> triggers) {
		this.triggers = triggers;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getTriggers()
	 */
	@Override
	public Map<String, Trigger> getTriggers() {
		return triggers;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#setEvents(java.util.Map)
	 */
	@Override
	public void setEvents(Map<String, Event> events) {
		this.events = events;
	}
	
	/* (non-Javadoc)
	 * @see gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence#getEvents()
	 */
	@Override
	public Map<String, Event> getEvents() {
		return events;
	}

}
