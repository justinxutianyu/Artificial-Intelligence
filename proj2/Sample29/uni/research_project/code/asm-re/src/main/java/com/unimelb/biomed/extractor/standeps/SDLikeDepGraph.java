package com.unimelb.biomed.extractor.standeps;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.dependency.DEPNode;
import com.googlecode.clearnlp.dependency.DEPTree;
import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;

import gov.nih.bnst.preprocessing.dp.DependencyGraph;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;
import edu.ucdenver.ccp.nlp.biolemmatizer.BioLemmatizer;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;

/** A dependency graph implementation which roughly emulates a Stanford Dependency tree */
public class SDLikeDepGraph implements DependencyGraph {
	private static final Logger LOG = LoggerFactory.getLogger(SDLikeDepGraph.class);

	private DirectedSparseGraph<Vertex, Edge> jungdg = null;
	private DEPTree originalClearTree = null;

	private static final Map<String, String> ESCAPES;
	private static final Pattern ESCAPE_PATTERN;
	private static final Set<String> POS_GENERALIZABLE;
	private static final BioLemmatizer bioLemmatizer = new BioLemmatizer();

	static {
		Map<String, String> m = new HashMap<String, String>();
		m.put("(", "-LRB-");
		m.put(")", "-RRB-");
		m.put(",", "-COMMA-");
		m.put("/", "-SLASH-");
		m.put("[", "-LSB-");
		m.put("]", "-RRB-");
		ESCAPES = Collections.unmodifiableMap(m);
		StringBuilder reBuild = new StringBuilder();
		for (String escd : ESCAPES.keySet()) {
			if (reBuild.length() > 0)
				reBuild.append("|");
			reBuild.append(Pattern.quote(escd));
		}
		ESCAPE_PATTERN = Pattern.compile(reBuild.toString());
		String[] posGen = { "NN", "NNS", "NNP", "NNPS", "VB", "VBD", "VBN", "VBZ", "VBP", "VBG",
				"JJ", "JJR", "JJS" };
		POS_GENERALIZABLE = Collections.unmodifiableSet(new HashSet<String>(Arrays.asList(posGen)));
	}

	protected final SortedMap<Integer, SDNode> nodes = new TreeMap<Integer, SDNode>();
	private final Map<Integer, Vertex> vertices = new HashMap<Integer, Vertex>();

	protected final List<SDLink> links = new ArrayList<SDLink>();

	private static final Pattern linkPattern = Pattern.compile("(\\w+)\\((" + SDNode.NODE_PATTERN
			+ "), (" + SDNode.NODE_PATTERN + ")\\)");

	public DEPTree getOriginalClearTree() {
		return originalClearTree;
	}

	public SDLikeDepGraph() {
	}

	public void addNode(int nodeId, String form, String pos) {
		addNode(new SDNode(nodeId, form, pos));
	}

	private void addNode(SDNode node) {
		nodes.put(node.getId(), node);
	}

	public SortedMap<Integer, SDNode> getNodes() {
		return nodes;
	}

	public List<SDLink> getLinks() {
		return links;
	}

	public void addLink(String label, int fromId, int toId) {
		links.add(new SDLink(label, fromId, toId, this));
	}

	private static String escape(String raw) {
		if (ESCAPE_PATTERN.matcher(raw).find()) {
			String escaped = raw;
			for (Map.Entry<String, String> ent : ESCAPES.entrySet())
				escaped = escaped.replace(ent.getKey(), ent.getValue());
			return escaped;
		} else {
			return raw;
		}
	}

	public SDLikeDepGraph(DEPTree clearTree) {
		for (DEPNode node : clearTree) {
			addNode(node.id, escape(node.form), escape(node.pos));
			LOG.trace("Adding new node with ID {}: {}/{}", node.id, node.form, node.pos);
			if (node.hasHead()) {
				addLink(node.getLabel(), node.getHead().id, node.id);
				LOG.trace("Adding new link {} --{}--> {}", node.id, node.getLabel(),
						node.getHead().id);
			}
			// XXX: not sure about all the business with semantic heads and dep
			// heads etc.
		}
		originalClearTree = clearTree;
	}

	public static SDLikeDepGraph fromSingleLine(String line) {
		SDLikeDepGraph tree = new SDLikeDepGraph();
		String[] linkComps = line.split("; ");
		for (String comp : linkComps) {
			Matcher matcher = linkPattern.matcher(comp);
			if (!matcher.matches())
				throw new TreeProcessingException("Could not match link '" + comp
						+ "' against pattern " + linkPattern.pattern());
			String linkLabel = matcher.group(1);
			String node1Rep = matcher.group(2);
			String node2Rep = matcher.group(2 + SDNode.NODE_PATTERN_NUM_GROUPS + 1);
			SDNode node1 = new SDNode(node1Rep);
			SDNode node2 = new SDNode(node2Rep);
			tree.addNode(node1);
			tree.addNode(node2);
			tree.addLink(linkLabel, node1.getId(), node2.getId());
		}
		return tree;
	}

	public String toString() {
		StringBuilder builder = new StringBuilder();
		for (SDLink link : links) {
			builder.append(link);
			builder.append("\n");
		}
		return builder.toString();
	}

	protected static class TreeProcessingException extends BnstRuntimeException {
		private static final long serialVersionUID = 1L;

		public TreeProcessingException(Throwable e) {
			super(e);
		}

		public TreeProcessingException(String st) {
			super(st);
		}
	}

	public DirectedGraph<Vertex, Edge> asJungDigraph() {
		if (jungdg != null)
			return jungdg;
		jungdg = new DirectedSparseGraph<Vertex, Edge>();

		Map<Integer, Vertex> tokenToNode = new HashMap<Integer, Vertex>();
		for (Integer nodeIdx : nodes.keySet()) {
			Vertex vertex = getVertex(nodeIdx);
			storeGeneralInfo(vertex);
			LOG.trace("Adding vertex {} to graph", vertex);
			jungdg.addVertex(vertex);
			tokenToNode.put(nodeIdx, vertex);
		}
		for (SDLink link : links) {
			Vertex from = tokenToNode.get(link.getFrom());
			Vertex to = tokenToNode.get(link.getTo());
			Edge edge = new Edge(from, link.getName(), to);
			jungdg.addEdge(edge, from, to);
		}
		return jungdg;
	}

	public SDNode getNode(Integer nodeIdx) {
		return nodes.get(nodeIdx);
	}

	public Vertex getVertex(Integer nodeIdx) {
		Vertex existing = vertices.get(nodeIdx);
		if (existing != null) {
			return existing;
		} else {
			Vertex newInst = new Vertex(nodes.get(nodeIdx).toString(), "withpos");
			if (originalClearTree != null)
				newInst.setOffset(originalClearTree.get(nodeIdx).span.begin);
			vertices.put(nodeIdx, newInst);
			return newInst;
		}
	}

	public Collection<SDNode> nodeList() {
		return nodes.values();
	}

	private static void storeGeneralInfo(Vertex node) {
		String lemma = node.getWord();
		if (lemma.length() > 1)
			lemma = lemma.replaceAll("-", "");
		if (lemma.matches("^BIO_Entity\\d*$"))
			lemma = "BIO_Entity";
		else
			lemma = bioLemmatizer.lemmatizeByLexiconAndRules(lemma, node.getPOSTag()).lemmasToString();
		lemma = lemma.replaceAll("\\d", "");
		lemma = lemma.toLowerCase();
		LOG.trace("Lemma for {} is {}", node.getWord(), lemma);
		node.setLemma(lemma);
		String tag = node.getPOSTag();
		if (POS_GENERALIZABLE.contains(tag))
			tag = tag.substring(0, 2); // NNPS -> NN etc
		// set compare form
        if (node.isArgument()) {
            node.setCompareForm(lemma.toLowerCase());
        } else {
            node.setCompareForm(tag.toLowerCase());
        }
        node.setGeneralizedPOS(tag);
	}

	@Override
	public DirectedGraph<Vertex, Edge> getGraph() {
		return asJungDigraph();
	}

	@Override
	public Vertex getNodeFromToken(String token) {
		String[] tokenComps = token.split("-", 2);
		Integer nodeId = new Integer(tokenComps[1]);
		return getVertex(nodeId);
	}

}
