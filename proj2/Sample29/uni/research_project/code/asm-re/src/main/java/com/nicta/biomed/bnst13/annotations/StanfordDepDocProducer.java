package com.nicta.biomed.bnst13.annotations;

import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.reader.StreamLineIterator;
import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst13.preprocessing.annotation.Anaphora;
import gov.nih.bnst13.preprocessing.annotation.Coreference;
import gov.nih.bnst13.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst13.preprocessing.annotation.Event;
import gov.nih.bnst13.preprocessing.annotation.Protein;
import gov.nih.bnst13.preprocessing.annotation.Trigger;
import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst13.preprocessing.combine.training.ReadSingleSentenceOutput;
import gov.nih.bnst13.preprocessing.dp.Edge;
import gov.nih.bnst13.preprocessing.dp.Vertex;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * <p>
 * Combining all related information for training data
 * </p>
 * 
 * @author Implemented and tested by Haibin Liu
 * 
 */
public class StanfordDepDocProducer implements DocumentProducer {
	/* adapted from gov.nih.bnst13.preprocessing.combine.testing.CombineInfo and
	 * gov.nih.bnst13.preprocessing.combine.training.CombineInfo
	 */
	
	private static final org.slf4j.Logger LOG = LoggerFactory.getLogger(StanfordDepDocProducer.class);
	
	/** path to the syntax tree directory */
	private static final String TREE_RELPATH = "trees";
	
	private static final Map<String, String> GRAPH_RELPATHS = new HashMap<String, String>();
	/** path to the dependency graph directory of McClosky_Charniak parser */
	private static final String GRAPH_MCC_RELPATH = "graphs";
	/** path to the dependency graph directory of Stanford parser */
	private static final String GRAPH_STANFORD_RELPATH = "graphs_stanford";
	static {
		GRAPH_RELPATHS.put("M", GRAPH_MCC_RELPATH);
		GRAPH_RELPATHS.put("S", GRAPH_STANFORD_RELPATH);
	}
	/** path to the offset directory */
	private static final String OFFSET_RELPATH = "offsets";
	/** the logger for suppressing the logger warning in StreamLineIterator */
	/** store all documents of the directory */
	Map<String, List<? extends AnnotatedSentence>> documents = new HashMap<String, List<? extends AnnotatedSentence>>();
	String graphPath;
	/** graph type to be retrieved: M stands for McClosky; S stands for Stanford */
	String graphType;
	/** store the last protein ID in each document for indexing triggers in later process */
	Map<String, Integer> lastProteinIDOfEachDocument = new HashMap<String, Integer>();

	private String annotationPath;

	private String offsetPath;

	private String treePath;

	/**
	 * Constructor to process all files in the task directory
	 */
	public StanfordDepDocProducer(String parseDataRoot, String annotationPath, String graphType) {
		this.graphType = graphType;
		this.annotationPath = annotationPath;
		setPaths(parseDataRoot);
		processSharedTaskDirectory();
	}

	public StanfordDepDocProducer(String parseDataRoot, String annotationPath) {
		this(parseDataRoot, annotationPath, "M");
	}

	private void setPaths(String parseDataRoot) {
		// TODO Auto-generated method stub
		String graphRelPath = GRAPH_RELPATHS.get(graphType);
		if (graphRelPath == null)
			throw new RuntimeException("Unknown graph type " + graphType);
		// read shared task directory and process each file in it
		graphPath = new File(parseDataRoot, graphRelPath).getAbsolutePath();
		offsetPath = new File(parseDataRoot, OFFSET_RELPATH).getAbsolutePath();
		treePath = new File(parseDataRoot, TREE_RELPATH).getAbsolutePath();
	}

	/**
	 * process the shared task file directory
	 */
	public void processSharedTaskDirectory() {
		File directory = new File(treePath);
		if (!directory.isDirectory()) {
			throw new RuntimeException("The provided diretory: " + directory.getAbsolutePath()
					+ " is not a directory. Please check.");
		}
		int fileCount = 0;
		for (File inputFile : directory.listFiles()) {
			if (!inputFile.isFile() || !inputFile.getName().matches("^\\S+\\.(pstree)$")) {
				continue;
			}
			// if(!inputFile.getName().equals("PMC-2222968-00-TIAB.pstree"))
			// continue;
			File treeFile = inputFile;
			// get the pmid
			String pmid = treeFile.getName().split("\\.")[0];
			File a1File = new File(annotationPath, pmid + ".a1");
			if (!a1File.exists()) {
				LOG.info("Ignoring parse file {} without corresponding a1 file at {}", inputFile, a1File);
				continue;
			}
			File graphFile = new File(graphPath, pmid + ".dep");
			File offsetFile = new File(offsetPath, pmid + ".offset");
			if (!graphFile.exists())
					throw new RuntimeException(
							"Detected tree file missing corresponding graph file: "
									+ treeFile.getAbsolutePath());
			if (!offsetFile.exists()) {
				throw new RuntimeException("Detected tree file missing corresponding offset file: "
						+ treeFile.getAbsolutePath() + " (offset file expected at: "
						+ offsetFile.getAbsolutePath() + ")");
			}
			System.out.println("processing ...... " + pmid + " the " + ++fileCount + " file.");
			List<ReadSingleSentenceOutput> document = processSingleDocument(treeFile, graphFile,
					offsetFile);
			// reading and processing annotation files: a1 and a2
			try {
				File a2File = new File(annotationPath, pmid + ".a2");
				// mapping from ProteinID to protein
				Map<String, Protein> proteinId2ProteinMap = readA1File(a1File);
				Map<String, ?>[] a2Annotation = readA2File(a2File);
				// mapping from triggerID to trigger
				Map<String, Trigger> triggerId2TriggerMap = (Map<String, Trigger>) a2Annotation[0];
				// mapping from eventID to event
				Map<String, Event> eventId2EventMap = (Map<String, Event>) a2Annotation[1];
				// mapping from anaphoraID to anaphora
				Map<String, Anaphora> anaphoraId2AnaphoraMap = (Map<String, Anaphora>) a2Annotation[2];
				// mapping from coreferenceID to coreference
				Map<String, Coreference> coreferenceId2CoreferenceMap = (Map<String, Coreference>) a2Annotation[3];

				for (AnnotatedSentence sentence : document) {
					// System.out.println("sentence " + sentence.getSentenceID()
					// + " " + sentence.getStartIndex() + " " +
					// sentence.getEndIndex());
					// associate gold annotations with each sentence, only about
					// protein, trigger and event
					associateGoldAnnotationWithEachSentence(sentence, proteinId2ProteinMap,
							triggerId2TriggerMap, eventId2EventMap, anaphoraId2AnaphoraMap,
							coreferenceId2CoreferenceMap);
					// associate sentence gold annotation with dependency graph
					associateSentenceGoldAnnotationWithDependencyGraph(sentence);
					/*
					 * // check the existence of special case: trigger and theme
					 * are in the same node if(sentence.getProteins() != null)
					 * for(String protein : sentence.getProteins().keySet()) {
					 * DepNodeVertex p =
					 * sentence.getProteins().get(protein).getGraphNode();
					 * if(sentence.getTriggers() != null) for(String trigger :
					 * sentence.getTriggers().keySet()) { Set<DepNodeVertex> v =
					 * sentence.getTriggers().get(trigger).getTriggerNodes();
					 * if(v.contains(p)) { System.out.println(protein + " " +
					 * trigger + " " + p); System.exit(1); } } }
					 */
				}
			} catch (IOException e) {
				e.printStackTrace();
				System.out.println(e.getMessage());
			}
			documents.put(pmid, document);
		}
	}

	/**
	 * associate provided gold annotation with each sentence
	 * 
	 * @param sentence
	 *            : the specific sentence
	 * @param proteinId2ProteinMap
	 *            : document-level mapping from protein id to protein
	 * @param triggerId2TriggerMap
	 *            : document-level mapping from trigger id to trigger
	 * @param eventId2EventMap
	 *            : document-level mapping from event id to event
	 * @param anaphoraId2AnaphoraMap
	 *            : document-level mapping from anaphora id to anaphora
	 * @param coreferenceId2CoreferenceMap
	 *            : document-level mapping from coreference id to coreference
	 */
	private void associateGoldAnnotationWithEachSentence(AnnotatedSentence sentence,
			Map<String, Protein> proteinId2ProteinMap, Map<String, Trigger> triggerId2TriggerMap,
			Map<String, Event> eventId2EventMap, Map<String, Anaphora> anaphoraId2AnaphoraMap,
			Map<String, Coreference> coreferenceId2CoreferenceMap) {
		Map<String, Protein> proteins = new HashMap<String, Protein>();
		for (Protein protein : proteinId2ProteinMap.values()) {
			if ((protein.getStartIndex() >= sentence.getStartIndex())
					&& ((protein.getEndIndex() < sentence.getEndIndex()) || (sentence.getEndIndex() == -1))) {
				proteins.put(protein.getProteinID(), protein);
			}
		}
		Map<String, Trigger> triggers = new HashMap<String, Trigger>();
		for (Trigger trigger : triggerId2TriggerMap.values()) {
			if ((trigger.getStartIndex() >= sentence.getStartIndex())
					&& ((trigger.getEndIndex() < sentence.getEndIndex()) || (sentence.getEndIndex() == -1))) {
				triggers.put(trigger.getTriggerID(), trigger);
			}
		}
		Map<String, Event> events = new HashMap<String, Event>();
		// first level check on individual events
		for (Event event : eventId2EventMap.values()) {
			// check first level trigger first
			if (!triggers.containsKey(event.getEventTrigger())) {
				continue;
			}
			// non-regulation events
			if (!event.getEventCategory().endsWith("egulation")) {
				// check Proteins
				boolean flag = false;
				for (String theme : event.getEventThemes()) {
					if (!proteins.containsKey(theme)) {
						flag = true;
						break;
					}
				}
				if (flag
						&& !checkAnaphoraAndCoreference(event, proteins, anaphoraId2AnaphoraMap,
								coreferenceId2CoreferenceMap, sentence))
					continue;
				events.put(event.getEventID(), event);
				continue;
			}
			// regulation related events
			// check theme
			if (event.getEventThemes().get(0).charAt(0) == 'E') {
				Set<String> triggerSet = new HashSet<String>();
				triggerSet = retrieveDeepestTriggerForEventArgument(triggerSet,
						eventId2EventMap.get(event.getEventThemes().get(0)), eventId2EventMap);
				boolean flag = false;
				for (String trigger : triggerSet) {
					if (!triggers.containsKey(trigger)) {
						flag = true;
						break;
					}
				}
				if (flag)
					continue;
			}
			// check Proteins
			else if (!proteins.containsKey(event.getEventThemes().get(0))
					&& !checkAnaphoraAndCoreference(event, proteins, anaphoraId2AnaphoraMap,
							coreferenceId2CoreferenceMap, sentence))
				continue;
			if (event.hasCause()) {
				// check cause
				if (event.getEventCause().charAt(0) == 'E') {
					Set<String> triggerSet = new HashSet<String>();
					triggerSet = retrieveDeepestTriggerForEventArgument(triggerSet,
							eventId2EventMap.get(event.getEventCause()), eventId2EventMap);
					boolean flag = false;
					for (String trigger : triggerSet) {
						if (!triggers.containsKey(trigger)) {
							flag = true;
							break;
						}
					}
					if (flag)
						continue;
				}
				// check Proteins
				else if (!proteins.containsKey(event.getEventCause())
						&& !checkAnaphoraAndCoreference(event, proteins, anaphoraId2AnaphoraMap,
								coreferenceId2CoreferenceMap, sentence))
					continue;
			}
			events.put(event.getEventID(), event);
		}
		// second level check on embedded events by means of loops
		Set<String> eventIDs;
		do {
			eventIDs = new HashSet<String>(events.keySet());
			for (String id : eventIDs) {
				Event event = events.get(id);
				if (event.getEventCategory().endsWith("egulation")) {
					if (event.getEventThemes().get(0).charAt(0) == 'E') {
						if (!eventIDs.contains(event.getEventThemes().get(0))) {
							events.remove(id);
							continue;
						}
					}
					if (event.hasCause() && event.getEventCause().charAt(0) == 'E') {
						if (!eventIDs.contains(event.getEventCause())) {
							events.remove(id);
							continue;
						}
					}
				}
			}
		} while (events.size() != eventIDs.size());

		if (proteins.size() != 0)
			sentence.setProteins(proteins);
		if (triggers.size() != 0)
			sentence.setTriggers(triggers);
		if (events.size() != 0)
			sentence.setEvents(events);
	}

	/**
	 * associate sentence gold annotation (proteins and triggers) with
	 * dependency graph
	 * 
	 * @param sentence
	 */
	private void associateSentenceGoldAnnotationWithDependencyGraph(AnnotatedSentence sentence) {
		// if no annotation, directly return
		if (sentence.getProteins() == null)
			return;
		// associate proteins
		for (String proteinID : sentence.getProteins().keySet()) {
			Protein protein = sentence.getProteins().get(proteinID);
			Set<Vertex> graphNodes = new HashSet<Vertex>();
			graphNodes = searchGraphNodeForAnnotationToken(protein.getStartIndex(),
					protein.getEndIndex(), sentence.getDependencyGraph().getGraph());
			Vertex centerNode = null;
			if (graphNodes.size() != 0) {
				// choose the center protein node in order to keep only one
				// graph node for each protein annotation
				centerNode = searchCenterNodeForAnnotationGraphNodes(graphNodes, sentence);
				if (centerNode == null) {
					throw new RuntimeException("There is no center node found for " + graphNodes);
				}
				// update protein vertex lemma to "BIO_Entity"
				// split node for special case: trigger and theme are in the
				// same node, normally separated by "-" in the node
				if (centerNode.getWord().length() != protein.getProteinName().length()) {
					String candidate = centerNode.getWord();
					// first replace protein with "BIO_Entity" in the String
					if (centerNode.getWord().length() > protein.getProteinName().length())
						candidate = candidate.replaceFirst(protein.getProteinName(), "BIO_Entity");
					else if (centerNode.getOffset() < protein.getEndIndex()) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = 0;
						int end = protein.getEndIndex() - centerNode.getOffset();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else if (centerNode.getOffset() + centerNode.getWord().length() > protein
							.getStartIndex()) {
						StringBuffer buffer = new StringBuffer(candidate);
						int start = protein.getStartIndex() - centerNode.getOffset();
						int end = centerNode.getWord().length();
						buffer.replace(start, end, "BIO_Entity");
						candidate = buffer.toString();
					} else
						throw new RuntimeException("checking centerNode " + centerNode
								+ " and protein " + protein.getProteinName());
					/*
					 * System.out.println("original centerNode " + centerNode +
					 * " " + proteinID + " " + candidate + " " +
					 * sentence.getDependencyGraph
					 * (graphType).getGraph().getEdgeCount() + " edges " +
					 * sentence
					 * .getDependencyGraph(graphType).getGraph().getVertexCount
					 * () + " nodes.");
					 */
					if (candidate.matches("\\S*BIO_Entity\\S+")) {
						Vertex v = new Vertex();
						String token = candidate.substring(candidate.indexOf("BIO_Entity") + 10);
						v.setCompareForm(token.toLowerCase());
						v.setTokenPosition(centerNode.getTokenPosition());
						v.setOffset(protein.getEndIndex());
						v.setToken(token);
						v.setWord(token);
						sentence.getDependencyGraph().getGraph().addVertex(v);
						Edge e = new Edge(centerNode, "dep", v);
						sentence.getDependencyGraph().getGraph().addEdge(e, centerNode, v);
						// System.out.println("New Node " + v);
					}
					if (candidate.matches("\\S+BIO_Entity\\S*")) {
						Vertex v = new Vertex();
						String token = candidate.substring(0, candidate.indexOf("BIO_Entity"));
						v.setCompareForm(token.toLowerCase());
						v.setTokenPosition(centerNode.getTokenPosition());
						v.setOffset(centerNode.getOffset());
						v.setToken(token);
						v.setWord(token);
						sentence.getDependencyGraph().getGraph().addVertex(v);
						Edge e = new Edge(centerNode, "dep", v);
						sentence.getDependencyGraph().getGraph().addEdge(e, centerNode, v);
						// System.out.println("New Node " + v);
					}
					List<Edge> inEdges = new ArrayList<Edge>();
					for (Edge e : sentence.getDependencyGraph().getGraph()
							.getInEdges(centerNode))
						inEdges.add(e);
					List<Edge> outEdges = new ArrayList<Edge>();
					for (Edge e : sentence.getDependencyGraph().getGraph()
							.getOutEdges(centerNode))
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
						sentence.getDependencyGraph().getGraph()
								.addEdge(e, e.getGovernor(), centerNode);
					for (Edge e : outEdges)
						sentence.getDependencyGraph().getGraph()
								.addEdge(e, centerNode, e.getDependent());
					// System.out.println("updated centerNode " + centerNode +
					// " " +
					// sentence.getDependencyGraph(graphType).getGraph().getEdgeCount()
					// + " edges " +
					// sentence.getDependencyGraph(graphType).getGraph().getVertexCount()
					// + " nodes.");
				} else
					centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
				// set DepNodeVertex fields
				centerNode.setIsProtein(true);
				centerNode.setProteinID(proteinID);
				// set Protein graph node field
				protein.setGraphNode(centerNode);
			}
		}
		// if no annotation, directly return
		if (sentence.getTriggers() == null)
			return;
		// associate triggers
		List<String> triggers = new ArrayList<String>(sentence.getTriggers().keySet());
		for (String triggerID : triggers) {
			Trigger trigger = sentence.getTriggers().get(triggerID);
			Set<Vertex> triggerNodes = new HashSet<Vertex>();
			triggerNodes = searchGraphNodeForAnnotationToken(trigger.getStartIndex(),
					trigger.getEndIndex(), sentence.getDependencyGraph().getGraph());
			if (triggerNodes.size() != 0) {
				for (Vertex v : triggerNodes) {
					// set DepNodeVertex fields
					v.setIsTrigger(true);
					v.setTriggerID(triggerID);
				}
				// set Protein graph node field
				trigger.setTriggerNodes(triggerNodes);
				Vertex centerNode = searchCenterNodeForAnnotationGraphNodes(triggerNodes, sentence);
				trigger.setTriggerCenterNode(centerNode);
				/*
				 * if(triggerNodes.size() > 1) {
				 * System.out.println("trigger nodes: " + triggerNodes);
				 * System.out.println("center node: " + centerNode); }
				 */
			} else {
				// remove trigger and remove events that use the trigger
				sentence.getTriggers().remove(triggerID);
				if (sentence.getEvents() != null) {
					// first level removal
					List<String> events = new ArrayList<String>(sentence.getEvents().keySet());
					for (String eventID : events) {
						if (sentence.getEvents().get(eventID).getEventTrigger().equals(triggerID))
							sentence.getEvents().remove(eventID);
					}
					// second level removal on embedded events by means of loops
					Set<String> eventIDs;
					do {
						eventIDs = new HashSet<String>(sentence.getEvents().keySet());
						for (String id : eventIDs) {
							Event event = sentence.getEvents().get(id);
							if (event.getEventCategory().endsWith("egulation")) {
								if (event.getEventThemes().get(0).charAt(0) == 'E') {
									if (!eventIDs.contains(event.getEventThemes().get(0))) {
										sentence.getEvents().remove(id);
										continue;
									}
								}
								if (event.hasCause() && event.getEventCause().charAt(0) == 'E') {
									if (!eventIDs.contains(event.getEventCause())) {
										sentence.getEvents().remove(id);
										continue;
									}
								}
							}
						}
					} while (sentence.getEvents().size() != eventIDs.size());
				}
				// throw new RuntimeException("checking " + triggerID +
				// " but got null!");
			}
		}
	}

	/**
	 * choose the center node in order to keep only one graph node for each
	 * annotation the criteria is based on the DepNodeVertex connectivity
	 * 
	 * @return
	 */
	private Vertex searchCenterNodeForAnnotationGraphNodes(Set<Vertex> graphNodes,
			AnnotatedSentence sentence) {
		// sort the graph nodes first from small position to big position
		List<Vertex> sorted = new ArrayList<Vertex>(graphNodes);
		Collections.sort(sorted, new MyComparator());
		// System.out.println("before sorting " + graphNodes);
		// System.out.println("after sorting " + sorted);
		Vertex centerNode = null;
		boolean flag = false;
		for (Vertex v : sorted) {
			Collection<Vertex> neighbors = sentence.getDependencyGraph().getGraph()
					.getNeighbors(v);
			for (Vertex n : neighbors) {
				if (!graphNodes.contains(n))
					flag = true;
			}
			if (flag) {
				centerNode = v;
				break;
			}
		}
		return centerNode;
	}

	/**
	 * search for the corresponding graph node of an annotation token
	 * 
	 * @param startIndex
	 * @param endIndex
	 * @param graph
	 * @return the found graph node
	 */
	private Set<Vertex> searchGraphNodeForAnnotationToken(int startIndex, int endIndex,
			DirectedGraph<Vertex, Edge> graph) {
		Set<Vertex> graphNodes = new HashSet<Vertex>();
		for (Vertex node : graph.getVertices()) {
			if ((node.getOffset() >= startIndex && node.getOffset() + node.getWord().length() <= endIndex)
					|| (node.getOffset() <= startIndex && node.getOffset()
							+ node.getWord().length() >= endIndex)
					|| (node.getOffset() < startIndex
							&& node.getOffset() + node.getWord().length() < endIndex && node
							.getOffset() + node.getWord().length() > startIndex)
					|| (node.getOffset() > startIndex
							&& node.getOffset() + node.getWord().length() > endIndex && node
							.getOffset() < endIndex)) {
				graphNodes.add(node);
			}
		}
		return graphNodes;
	}

	/**
	 * handle anaphora and coreference annotations
	 * 
	 * @param proteinId2ProteinMap
	 * @param eventId2EventMap
	 * @param anaphoraId2AnaphoraMap
	 * @param coreferenceId2CoreferenceMap
	 */
	private boolean checkAnaphoraAndCoreference(Event event, Map<String, Protein> proteins,
			Map<String, Anaphora> anaphoraId2AnaphoraMap,
			Map<String, Coreference> coreferenceId2CoreferenceMap, AnnotatedSentence sentence) {
		boolean hasAnorphora = false;
		// handle anaphora and coreference annotation
		for (String coreferenceID : coreferenceId2CoreferenceMap.keySet()) {
			String anaphora = coreferenceId2CoreferenceMap.get(coreferenceID)
					.getCoreferenceSubject();
			String protein = coreferenceId2CoreferenceMap.get(coreferenceID).getCoreferenceObject();
			for (int i = 0; i < event.getEventThemes().size(); i++) {
				String theme = event.getEventThemes().get(i);
				if (theme.equals(protein)
						&& anaphoraId2AnaphoraMap.get(anaphora).getStartIndex() >= sentence
								.getStartIndex()
						&& anaphoraId2AnaphoraMap.get(anaphora).getEndIndex() < sentence
								.getEndIndex()) {
					// add anaphora as protein
					String line = anaphoraId2AnaphoraMap.get(anaphora).toA2String();
					line = line.replaceFirst("Anaphora", "Protein");
					Protein anaphoraToProtein = new Protein(line);
					proteins.put(anaphoraToProtein.getProteinID(), anaphoraToProtein);
					// update event with coreference
					event.getEventThemes().set(i, anaphora);
					hasAnorphora = true;
				}
			}
			if (event.hasCause()
					&& event.getEventCause().equals(protein)
					&& anaphoraId2AnaphoraMap.get(anaphora).getStartIndex() >= sentence
							.getStartIndex()
					&& anaphoraId2AnaphoraMap.get(anaphora).getEndIndex() < sentence.getEndIndex()) {
				// add anaphora as protein
				String line = anaphoraId2AnaphoraMap.get(anaphora).toA2String();
				line = line.replaceFirst("Anaphora", "Protein");
				Protein anaphoraToProtein = new Protein(line);
				proteins.put(anaphoraToProtein.getProteinID(), anaphoraToProtein);
				// update event with coreference
				event.setCause(anaphora);
				hasAnorphora = true;
			}
		}
		return hasAnorphora;
	}

	/**
	 * recursively to retrieve the trigger at the deepest level of a event chain
	 * 
	 * @param event
	 * @param triggerId2TriggerMap
	 * @param eventId2EventMap
	 * @return
	 */
	private static Set<String> retrieveDeepestTriggerForEventArgument(Set<String> triggers,
			Event event, Map<String, Event> eventId2EventMap) {
		if (!event.hasCause()) {
			if (event.getEventThemes().get(0).charAt(0) == 'E')
				triggers = retrieveDeepestTriggerForEventArgument(triggers,
						eventId2EventMap.get(event.getEventThemes().get(0)), eventId2EventMap);
		} else {
			if (event.getEventThemes().get(0).charAt(0) == 'E')
				triggers = retrieveDeepestTriggerForEventArgument(triggers,
						eventId2EventMap.get(event.getEventThemes().get(0)), eventId2EventMap);
			if (event.getEventCause().charAt(0) == 'E')
				triggers = retrieveDeepestTriggerForEventArgument(triggers,
						eventId2EventMap.get(event.getEventCause()), eventId2EventMap);
		}
		triggers.add(event.getEventTrigger());
		return triggers;
	}

	/**
	 * method to process a single document and combine all the useful
	 * information including both generated information and gold annotations
	 */
	private List<ReadSingleSentenceOutput> processSingleDocument(File treeFile, File graphFile, File offsetFile) {
		List<ReadSingleSentenceOutput> document = new ArrayList<ReadSingleSentenceOutput>();
		try {
			List<String> trees = readTreeFile(treeFile);
			List<String> allGraphs = readGraphFile(graphFile);
			List<List<Integer>> offsets = readOffsetFile(offsetFile);

			//iterate each sentence in the document
			for(int i = 0; i < trees.size(); i++) {
				//System.out.println("This is the #" + (i+1) + " sentence." );
				int endIndex;
				//compute the sentence end index
				if(i == trees.size()-1)
					endIndex = -1;
				else
					endIndex = offsets.get(i+1).get(0);
				ReadSingleSentenceOutput singleSentenceOutput = new ReadSingleSentenceOutput(
						i+1, endIndex, trees.get(i), offsets.get(i), allGraphs.get(i));
				document.add(singleSentenceOutput);
			}		
		}catch(IOException e) {
			e.printStackTrace();
			System.out.println(e.getMessage());
		}
		return document; 
	}

	/**
	 * @param treeFile
	 *            input file in the PennTree bank style tree format
	 * @return a list of trees
	 * @throws IOException
	 */
	private static List<String> readTreeFile(File treeFile) throws IOException {
		if (!treeFile.getName().matches("^\\S+\\.(pstree)$")) {
			throw new RuntimeException(
					"invalid syntax tree file! Should end with suffix \"pstree\" "
							+ treeFile.getName());
		}
		List<String> pennTrees = new ArrayList<String>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(treeFile, CharacterEncoding.UTF_8, null);
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				pennTrees.add(line);
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return pennTrees;
	}

	/**
	 * @param offsetFile
	 *            input file in the offset format
	 * @return a list of sentence offsets
	 * @throws IOException
	 */
	private static List<List<Integer>> readOffsetFile(File offsetFile) throws IOException {
		if (!offsetFile.getName().matches("^\\S+\\.(offset)$")) {
			throw new RuntimeException("invalid offset file! Should end with suffix \"offset\" "
					+ offsetFile.getName());
		}
		List<List<Integer>> offsets = new ArrayList<List<Integer>>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(offsetFile, CharacterEncoding.UTF_8, null);
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				List<Integer> sentenceOffsets = new ArrayList<Integer>();
				// convert each offset string into integer
				for (String offset : split(line, " "))
					sentenceOffsets.add(Integer.parseInt(offset));
				offsets.add(sentenceOffsets);
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return offsets;
	}

	/**
	 * @param graphFile
	 *            input file in the dependency graph format
	 * @return a list of sentence graphs
	 * @throws IOException
	 */
	private static List<String> readGraphFile(File graphFile) throws IOException {
		if (!graphFile.getName().matches("^\\S+\\.(dep)$")) {
			throw new RuntimeException(
					"invalid dependency graph file! Should end with suffix \"dep\" "
							+ graphFile.getName());
		}
		List<String> graphs = new ArrayList<String>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(graphFile, CharacterEncoding.UTF_8, null);
			List<String> representations = new ArrayList<String>();
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				if (line.trim().length() == 0) {
					graphs.add(join(representations, "\t"));
					representations.clear();
				} else
					representations.add(line.trim());
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return graphs;
	}

	/**
	 * @param a1File
	 *            input file in the BioNLP '09 .a1 file format
	 * @return mapping from protein ID, e.g.T5, to the {@link Protein} itself
	 * @throws IOException
	 */
	private Map<String, Protein> readA1File(File a1File) throws IOException {
		Map<String, Protein> proteinAnnotation = new HashMap<String, Protein>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(a1File, CharacterEncoding.UTF_8, null);
			String lastProteinID = null;
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				if (!line.matches("^(T\\d+)\\tProtein\\s(\\d+)\\s(\\d+)\\t(.+)$")) {
					throw new RuntimeException("The protein record: " + line + " is not valid. Please check.");
				}
				Protein protein = new Protein(line);
				proteinAnnotation.put(protein.getProteinID(), protein);
				lastProteinID = protein.getProteinID();
			}
			String pmid = a1File.getName().split("\\.")[0];
			if(lastProteinID != null)
			    lastProteinIDOfEachDocument.put(pmid, Integer.parseInt(lastProteinID.substring(1))); 
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return proteinAnnotation;
	}
	/**
	 * @param a2File
	 *            input file in the BioNLP '09 .a2 file format
	 * @return mapping from event ID, e.g.E5, to the {@link Event} itself
	 * @throws IOException
	 */
	private static Map<String, ?>[] readA2File(File a2File) throws IOException {
		Map<String, Trigger> triggerAnnotation = new HashMap<String, Trigger>();
		Map<String, Event> eventAnnotation = new HashMap<String, Event>();
		Map<String, Anaphora> anaphoraAnnotation = new HashMap<String, Anaphora>();
		Map<String, Coreference> coreferenceAnnotation = new HashMap<String, Coreference>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(a2File, CharacterEncoding.UTF_8, null);
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				// handle Anaphora and Coreference annotation in 2013 task
				if (line.matches("^(T\\d+)\\t(Anaphora)\\s(\\d+)\\s(\\d+)\\t(.+)$")) {
					Anaphora anaphora = new Anaphora(line);
					anaphoraAnnotation.put(anaphora.getAnaphoraID(), anaphora);
				} else if (line.matches("^(T\\d+)\\t(\\w+)\\s(\\d+)\\s(\\d+)\\t(.+)$")) {
					Trigger trigger = new Trigger(line);
					triggerAnnotation.put(trigger.getTriggerID(), trigger);
				} else if (line.charAt(0) == 'E') {
					Event event = new Event(line);
					eventAnnotation.put(event.getEventID(), event);
				} else if (line.charAt(0) == 'R') {
					Coreference coreference = new Coreference(line);
					coreferenceAnnotation.put(coreference.getCoreferenceID(), coreference);
				} else if (line.charAt(0) == 'M' || line.charAt(0) == '*') { // modification / Equiv
					continue;
				} else {
					throw new RuntimeException("The A2 file record: " + line
							+ " is not valid. Please check.");
				}
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}

		return new Map[] { triggerAnnotation, eventAnnotation, anaphoraAnnotation,
				coreferenceAnnotation };
	}

	/**
	 * s compact DIY string splitting method
	 * 
	 * @param s
	 *            : string to split
	 * @param separator
	 *            : separator for the string to be split on
	 * @return a list of split substrings
	 */
	public static final List<String> split(final String s, final String separator) {
		int lastIndex = 0, currentIndex = 0;
		List<String> strArray = new ArrayList<String>();
		while ((currentIndex = s.indexOf(separator, lastIndex)) != -1) {
			strArray.add(s.substring(lastIndex, currentIndex));
			lastIndex = currentIndex + separator.length();
		}
		if (s.substring(lastIndex).length() != 0)
			strArray.add(s.substring(lastIndex));
		return strArray;
	}

	/**
	 * static method to concatenate String items with a specified delimiter
	 * 
	 * @param s
	 * @param delimiter
	 * @return concatenated String items with a specified delimiter
	 */
	public static final String join(Collection<String> s, String delimiter) {
		if (s.isEmpty()) {
			return "";
		}
		Iterator<String> iter = s.iterator();
		StringBuffer buffer = new StringBuffer(iter.next());
		while (iter.hasNext()) {
			buffer.append(delimiter).append(iter.next());
		}
		return buffer.toString();
	}

	/**
	 * retrieve fully annotated documents combined with dependency graphs
	 * 
	 * @return documents
	 */
	public Map<String, List<? extends AnnotatedSentence>> getAnnotatedDocuments() {
		return documents;
	}

	@Override
	public Map<String, List<? extends AnnotatedSentence>> getIdsToAnnotatedSentences() {        
		return new HashMap<String, List<? extends AnnotatedSentence>>(documents);
    }
		
	/**
	 * retrieve last protein ID of all documents
	 * @return lastProteinIDOfEachDocument
	 */
	public Map<String, Integer> getLastProteinIDOfDocuments() {
		return lastProteinIDOfEachDocument;
	}
	
	private class SDAnnDocImpl implements AnnotatedDocument {
		private final String id;
		private final List<? extends AnnotatedSentence> annSents;
		private final Integer lastProtId;
		
		public SDAnnDocImpl(String id, List<? extends AnnotatedSentence> list, Integer lastProtId) {
			this.id = id;
			this.annSents = list;
			this.lastProtId = lastProtId;
		}

		@Override
		public String getId() {
			return id;
		}

		@Override
		public List<? extends AnnotatedSentence> getAnnSentences() {
			return annSents;
		}

		@Override
		public int getLastProteinId() {
			return lastProtId != null ? lastProtId.intValue() : -1;
		}
		
	}

	@Override
	public Iterable<AnnotatedDocument> documents() {
		List<AnnotatedDocument> docs = new ArrayList<AnnotatedDocument>();
		for (Map.Entry<String, ? extends List<? extends AnnotatedSentence>> docSents : documents.entrySet()) {
			String docId = docSents.getKey();
			docs.add(new SDAnnDocImpl(docId, docSents.getValue(), lastProteinIDOfEachDocument.get(docId)));
		}
		return docs;
	}
}

class MyComparator implements Comparator<Vertex> {
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
