package com.unimelb.biomed.extractor.learning;

import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst.patternlearning.EventRule;
import gov.nih.bnst.patternlearning.RelationRule;
import gov.nih.bnst.preprocessing.annotation.Argument;
import gov.nih.bnst.preprocessing.annotation.Event;
import gov.nih.bnst.preprocessing.annotation.Protein;
import gov.nih.bnst.preprocessing.annotation.Relation;
import gov.nih.bnst.preprocessing.annotation.Trigger;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class GenAnnotatedSentence implements AnnotatedSentence {
	private static final Logger LOG = LoggerFactory.getLogger(GenAnnotatedSentence.class);

	/** sentence ID */
	private int sentenceID;

	/** proteins that belong to the sentence */
	private Map<String, Protein> proteins = null;

    /** triggers that belong to the sentence */
	private Map<String, Trigger> triggers = null;

    /** arguments that belong to the sentence */
    private Map<String, Argument> arguments = null;

    /** events that belong to the sentence */
	private Map<String, Event> events = null;

    /** relations that belong to the sentence */
	private Map<String, Relation> relations = null;

    /** event rules of the sentence */
	private List<EventRule> eventRulesOfSentence;

    /** event rules of the sentence */
	private List<RelationRule> relationRulesOfSentence;

	public GenAnnotatedSentence(int sentenceID) {
		this.sentenceID = sentenceID;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getSentenceID()
	 */
	@Override
	public int getSentenceID() {
		return sentenceID;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getStartIndex()
	 */
	@Override
	abstract public int getStartIndex();

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getEndIndex()
	 */
	@Override
	abstract public int getEndIndex();

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getEventRulesOfSentence()
	 */
	@Override
	public List<EventRule> getEventRulesOfSentence() {
		return eventRulesOfSentence;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#setEventRulesOfSentence(java.util.List)
	 */
	@Override
	public void setEventRulesOfSentence(List<EventRule> eventRulesOfSentence) {
		this.eventRulesOfSentence = eventRulesOfSentence;
	}

    @Override
	public List<RelationRule> getRelationRulesOfSentence() {
		return relationRulesOfSentence;
	}

    @Override
	public void setRelationRulesOfSentence(List<RelationRule> relationRulesOfSentence) {
		this.relationRulesOfSentence = relationRulesOfSentence;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#setProteins(java.util.Map)
	 */
	@Override
	public void setProteins(Map<String, Protein> proteins) {
		this.proteins = proteins;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getProteins()
	 */
	@Override
	public Map<String, Protein> getProteins() {
		return proteins;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#setTriggers(java.util.Map)
	 */
	@Override
	public void setTriggers(Map<String, Trigger> triggers) {
		this.triggers = triggers;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getTriggers()
	 */
	@Override
	public Map<String, Trigger> getTriggers() {
		return triggers;
	}

	public void setArguments(Map<String, Argument> arguments) {
		this.arguments = arguments;
	}

	public Map<String, Argument> getArguments() {
		return arguments;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#setEvents(java.util.Map)
	 */
	@Override
	public void setEvents(Map<String, Event> events) {
		this.events = events;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getEvents()
	 */
	@Override
	public Map<String, Event> getEvents() {
		return events;
	}

    /* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#setEvents(java.util.Map)
	 */
	public void setRelations(Map<String, Relation> relations) {
		this.relations = relations;
	}

	/* (non-Javadoc)
	 * @see gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence#getEvents()
	 */
	public Map<String, Relation> getRelations() {
		return relations;
	}

	/**
	 * choose the center node in order to keep only one graph node for each annotation
	 * the criteria is based on the Vertex connectivity
	 * @return
	 */
	public Vertex findCenterNode(Set<Vertex> graphNodes) {
		//sort the graph nodes first from small position to big position
		List<Vertex> sorted = new ArrayList<Vertex>(graphNodes);
		Collections.sort(sorted, new VertexComparator());
		Vertex centerNode = null;
		boolean flag = false;
    	for(Vertex v : sorted) {
			Collection<Vertex> neighbors = getDependencyGraph().getGraph().getNeighbors(v);
			if (neighbors == null) {
				LOG.warn("Node {} not found in graph", v);
				continue;
			}

			for(Vertex n : neighbors) {
				if(!graphNodes.contains(n))
					flag = true;
			}
			if(flag) { centerNode = v; break; }
		}
    	return centerNode;
	}


	/**
	 * search for the corresponding graph node of an annotation token
	 * @param startIndex
	 * @param endIndex
	 * @param graph
	 * @return the found graph node
	 */
	protected Set<Vertex> searchGraphNodeForAnnotationToken(int startIndex, int endIndex) {
		Set<Vertex> graphNodes = new HashSet<Vertex>();
		for(Vertex node : getDependencyGraph().getGraph().getVertices()) {
			if( (node.getOffset() >= startIndex &&
					node.getOffset() + node.getWord().length() <= endIndex) ||
				(node.getOffset() <= startIndex &&
					node.getOffset() + node.getWord().length() >= endIndex) ||
				(node.getOffset() < startIndex &&
					node.getOffset() + node.getWord().length() < endIndex &&
					node.getOffset() + node.getWord().length() > startIndex) ||
				(node.getOffset() > startIndex &&
					node.getOffset() + node.getWord().length() > endIndex &&
					node.getOffset() < endIndex)
			) {
				graphNodes.add(node);
			}
		}
		return graphNodes;
	}

	/**
	 * associate sentence gold annotation (proteins and triggers) with
	 * dependency graph
	 *
	 * @param sentence
	 */
	public void postprocessProteinNodes() {
		// if no annotation, directly return
		if (getProteins() == null)
			return;
		// associate proteins
		for (String proteinID : getProteins().keySet()) {
			Protein protein = getProteins().get(proteinID);
			Set<Vertex> graphNodes = new HashSet<Vertex>();
			graphNodes = searchGraphNodeForAnnotationToken(protein.getStartIndex(),
					protein.getEndIndex());
			Vertex centerNode = null;
			if (graphNodes.size() != 0) {
				// choose the center protein node in order to keep only one
				// graph node for each protein annotation
				centerNode = findCenterNode(graphNodes);
				//if (centerNode == null)
				//	throw new RuntimeException("There is no center node found for " + graphNodes);

				if (centerNode == null)
                                {
				//	throw new RuntimeException("There is no center node found for " + graphNodes);
                                  LOG.warn("There is no center node found for " + graphNodes);
                                  continue;
                                }
				// update protein vertex lemma to "BIO_Entity"
				// split node for special case: trigger and theme are in the
				// same node, normally separated by "-" in the node
				if (centerNode.getProteinID() != null
						&& !centerNode.getProteinID().equals(proteinID))
					LOG.info("Center node {}@{} is already attached to protein ID {} "
							+ "while trying to match new protein {}@{}:{}", centerNode,
							centerNode.getOffset(), centerNode.getProteinID(), proteinID,
							protein.getStartIndex(), protein.getEndIndex());
				if (centerNode.getWord().length() == protein.getProteinName().length()
						|| ((centerNode.getOffset() >= protein.getStartIndex()) && centerNode
								.getOffset() + centerNode.getWord().length() <= protein
									.getEndIndex())) {
					centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
				} else {
					String candidate = centerNode.getWord();
					// first replace protein with "BIO_Entity" in the String
					if ((centerNode.getOffset() <= protein.getStartIndex())
							&& centerNode.getOffset() + centerNode.getWord().length() >= protein
									.getEndIndex()) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = protein.getStartIndex() - centerNode.getOffset();
						int end = protein.getEndIndex() - centerNode.getOffset();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else if ((centerNode.getOffset() < protein.getEndIndex())
							&& (centerNode.getOffset() > protein.getStartIndex())) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = 0;
						int end = protein.getEndIndex() - centerNode.getOffset();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else if ((centerNode.getOffset() + centerNode.getWord().length() > protein
							.getStartIndex()) && (centerNode.getOffset() < protein.getStartIndex())) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = protein.getStartIndex() - centerNode.getOffset();
						int end = centerNode.getWord().length();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else
						throw new RuntimeException("checking centerNode " + centerNode
								+ " and protein " + protein.getProteinName());
					LOG.trace("original centerNode {} {} {} edges: {}, nodes: {}", centerNode,
							proteinID, candidate, getDependencyGraph().getGraph().getEdgeCount(),
							getDependencyGraph().getGraph().getVertexCount());
					if (candidate.matches("\\S*BIO_Entity\\S+")) {
						Vertex v = new Vertex();
						String token = candidate.substring(candidate.indexOf("BIO_Entity") + 10);
						v.setCompareForm(token.toLowerCase());
						v.setTokenPosition(centerNode.getTokenPosition());
						v.setOffset(protein.getEndIndex());
						v.setToken(token);
						v.setWord(token);
						getDependencyGraph().getGraph().addVertex(v);
						Edge e = new Edge(centerNode, "dep", v);
						getDependencyGraph().getGraph().addEdge(e, centerNode, v);
						LOG.trace("New pre-Node: {} ", v);
					}
					if (candidate.matches("\\S+BIO_Entity\\S*")) {
						Vertex v = new Vertex();
						String token = candidate.substring(0, candidate.indexOf("BIO_Entity"));
						v.setCompareForm(token.toLowerCase());
						v.setTokenPosition(centerNode.getTokenPosition());
						v.setOffset(centerNode.getOffset());
						v.setToken(token);
						v.setWord(token);
						getDependencyGraph().getGraph().addVertex(v);
						Edge e = new Edge(centerNode, "dep", v);
						getDependencyGraph().getGraph().addEdge(e, centerNode, v);
						LOG.trace("New post-Node: {} ", v);
					}
					List<Edge> inEdges = new ArrayList<Edge>();
					for (Edge e : getDependencyGraph().getGraph().getInEdges(centerNode))
						inEdges.add(e);
					List<Edge> outEdges = new ArrayList<Edge>();
					for (Edge e : getDependencyGraph().getGraph().getOutEdges(centerNode))
						outEdges.add(e);
					// finally update the current vertex info
					centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
					centerNode.setOffset(protein.getStartIndex());
					centerNode.setToken(protein.getProteinName() + "-"
							+ centerNode.getTokenPosition());
					centerNode.setWord(protein.getProteinName());
					// resign the edges to centerNode due to the change of the
					// hashcode keys of centerNode above
					for (Edge e : inEdges)
						getDependencyGraph().getGraph().addEdge(e, e.getGovernor(), centerNode);
					for (Edge e : outEdges)
						getDependencyGraph().getGraph().addEdge(e, centerNode, e.getDependent());
				}
				centerNode.setIsProtein(true);
				centerNode.setProteinID(proteinID);
				// set Protein graph node field
				protein.setGraphNode(centerNode);
			}
		}
	}

    /**
	 * associate sentence gold annotation (arguments) with
	 * dependency graph
	 *
	 * @param sentence
	 */
	public void postprocessArgumentNodes() {
		// if no annotation, directly return
		if (getProteins() == null)
			return;

        // Associate arguments
		for (String argumentID : getArguments().keySet()) {
			Argument argument = getArguments().get(argumentID);

            Set<Vertex> graphNodes = new HashSet<Vertex>();
			graphNodes =
                searchGraphNodeForAnnotationToken(
                    argument.getStartIndex(),
					argument.getEndIndex()
                );

            Vertex centerNode = null;

            if (graphNodes.size() != 0) {
				// choose the center argument node in order to keep only one
				// graph node for each argument annotation
				centerNode = findCenterNode(graphNodes);
				//if (centerNode == null)
				//	throw new RuntimeException("There is no center node found for " + graphNodes);

				if (centerNode == null) {
				//	throw new RuntimeException("There is no center node found for " + graphNodes);
                    LOG.warn("There is no center node found for " + graphNodes);
                    continue;
                }
				// update argument vertex lemma to "BIO_Entity"
				// split node for special case: trigger and theme are in the
				// same node, normally separated by "-" in the node
				if (
                    centerNode.getArgumentID() != null &&
                    !centerNode.getArgumentID().equals(argumentID)
                ) {
                    LOG.info(
                        "Center node {}@{} is already attached " +
                        "to argument ID {} while trying to match " +
                        "new argument {}@{}:{}",
                        centerNode, centerNode.getOffset(),
                        centerNode.getArgumentID(), argumentID,
						argument.getStartIndex(), argument.getEndIndex()
                    );
                }
				if (
                    centerNode.getWord().length() == argument.getArgumentName().length()
					|| (
                        (centerNode.getOffset() >= argument.getStartIndex())
                        && ((centerNode.getOffset() + centerNode.getWord().length()) <= argument.getEndIndex())
                    )
                ) {
					centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
				} else {
					String candidate = centerNode.getWord();
					// first replace argument with "BIO_Entity" in the String
					if ((centerNode.getOffset() <= argument.getStartIndex())
							&& centerNode.getOffset() + centerNode.getWord().length() >= argument
									.getEndIndex()) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = argument.getStartIndex() - centerNode.getOffset();
						int end = argument.getEndIndex() - centerNode.getOffset();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else if ((centerNode.getOffset() < argument.getEndIndex())
							&& (centerNode.getOffset() > argument.getStartIndex())) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = 0;
						int end = argument.getEndIndex() - centerNode.getOffset();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else if ((centerNode.getOffset() + centerNode.getWord().length() > argument
							.getStartIndex()) && (centerNode.getOffset() < argument.getStartIndex())) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = argument.getStartIndex() - centerNode.getOffset();
						int end = centerNode.getWord().length();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else
						throw new RuntimeException("checking centerNode " + centerNode
								+ " and argument " + argument.getArgumentName());
					LOG.trace("original centerNode {} {} {} edges: {}, nodes: {}", centerNode,
							argumentID, candidate, getDependencyGraph().getGraph().getEdgeCount(),
							getDependencyGraph().getGraph().getVertexCount());
					if (candidate.matches("\\S*BIO_Entity\\S+")) {
						Vertex v = new Vertex();
						String token = candidate.substring(candidate.indexOf("BIO_Entity") + 10);
						v.setCompareForm(token.toLowerCase());
						v.setTokenPosition(centerNode.getTokenPosition());
						v.setOffset(argument.getEndIndex());
						v.setToken(token);
						v.setWord(token);
						getDependencyGraph().getGraph().addVertex(v);
						Edge e = new Edge(centerNode, "dep", v);
						getDependencyGraph().getGraph().addEdge(e, centerNode, v);
						LOG.trace("New pre-Node: {} ", v);
					}
					if (candidate.matches("\\S+BIO_Entity\\S*")) {
						Vertex v = new Vertex();
						String token = candidate.substring(0, candidate.indexOf("BIO_Entity"));
						v.setCompareForm(token.toLowerCase());
						v.setTokenPosition(centerNode.getTokenPosition());
						v.setOffset(centerNode.getOffset());
						v.setToken(token);
						v.setWord(token);
						getDependencyGraph().getGraph().addVertex(v);
						Edge e = new Edge(centerNode, "dep", v);
						getDependencyGraph().getGraph().addEdge(e, centerNode, v);
						LOG.trace("New post-Node: {} ", v);
					}
					List<Edge> inEdges = new ArrayList<Edge>();
					for (Edge e : getDependencyGraph().getGraph().getInEdges(centerNode))
						inEdges.add(e);
					List<Edge> outEdges = new ArrayList<Edge>();
					for (Edge e : getDependencyGraph().getGraph().getOutEdges(centerNode))
						outEdges.add(e);
					// finally update the current vertex info
					centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
					centerNode.setOffset(argument.getStartIndex());
					centerNode.setToken(argument.getArgumentName() + "-"
							+ centerNode.getTokenPosition());
					centerNode.setWord(argument.getArgumentName());
					// resign the edges to centerNode due to the change of the
					// hashcode keys of centerNode above
					for (Edge e : inEdges)
						getDependencyGraph().getGraph().addEdge(e, e.getGovernor(), centerNode);
					for (Edge e : outEdges)
						getDependencyGraph().getGraph().addEdge(e, centerNode, e.getDependent());
				}
				centerNode.setIsArgument(true);
				centerNode.setArgumentID(argumentID);
				// set Argument graph node field
				argument.setGraphNode(centerNode);
			}
		}
	}

}



class VertexComparator implements Comparator<Vertex> {
	@Override
	public int compare(Vertex o1, Vertex o2) {
		if (o1.getTokenPosition() < o2.getTokenPosition()) {
			return 1;
		} else if (o1.getTokenPosition() > o2.getTokenPosition()) {
			return -1;
		}
		return 0;
	}
}
