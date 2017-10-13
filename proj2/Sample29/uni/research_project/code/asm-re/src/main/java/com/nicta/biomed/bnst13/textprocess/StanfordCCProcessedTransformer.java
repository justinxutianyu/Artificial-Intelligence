package com.nicta.biomed.bnst13.textprocess;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;

import edu.northwestern.at.utils.math.rootfinders.Bisection;
import edu.stanford.nlp.international.Languages.Language;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.ling.Word;
import edu.stanford.nlp.trees.EnglishGrammaticalRelations;
import edu.stanford.nlp.trees.EnglishGrammaticalStructure;
import edu.stanford.nlp.trees.EnglishGrammaticalStructureFactory;
import edu.stanford.nlp.trees.GrammaticalRelation;
import edu.stanford.nlp.trees.TreeGraphNode;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.util.Pair;
import edu.uci.ics.jung.graph.DirectedGraph;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import gov.nih.bnst13.preprocessing.dp.Edge;
import gov.nih.bnst13.preprocessing.dp.Vertex;

public class StanfordCCProcessedTransformer implements GraphTransformer {
	public static Logger LOG = LoggerFactory.getLogger(StanfordCCProcessedTransformer.class);
	@Override
	public DirectedGraph<Vertex, Edge> transform(DirectedGraph<Vertex, Edge> orig) {
		LOG.debug("Original graph is {}", orig);
		JungToSDBidiConverter conv = new JungToSDBidiConverter(orig);
		Pair<TreeGraphNode, List<TypedDependency>> asSD = conv.getNativeStanfordDeps();
		LOG.debug("Found root node {} and deps {}", asSD.first(), asSD.second());
		EnglishGrammaticalStructure egs = new EnglishGrammaticalStructure(asSD.second(), asSD.first());
		Collection<TypedDependency> ccproc = egs.typedDependenciesCCprocessed();
		DirectedGraph<Vertex, Edge> ccprocJung = conv.reconvertToJung(ccproc);
		LOG.debug("CCPropagated graph is {}", ccprocJung);
		return ccprocJung;
	}
	
	
	protected static class JungToSDBidiConverter {
		/** Labels we get from ClearNLP which SD doesn't know about */
		static Map<String, String> CLEAR_TO_SD_LABELS = new HashMap<String, String>();
		/** Labels which may only be in the SD form because we were require to map them */
		static Set<String> POSSIBLE_REMAPPED_LABELS = new HashSet<String>();
		static String DEFAULT_LABEL = "dep";
		
		static {
			CLEAR_TO_SD_LABELS.put("hmod", "amod"); // hyphen modification => adjective mod'n
			CLEAR_TO_SD_LABELS.put("nmod", "amod"); //nominial mod'n => adjectival
			POSSIBLE_REMAPPED_LABELS.addAll(CLEAR_TO_SD_LABELS.values());
			POSSIBLE_REMAPPED_LABELS.add(DEFAULT_LABEL);
		}
		
		Map<Vertex, TreeGraphNode> sdNodes = new HashMap<Vertex, TreeGraphNode>();
		Map<Integer, Vertex> originalVerticesByIndex = new HashMap<Integer, Vertex>();
		
		DirectedGraph<Vertex, Edge> jungGraph;
		
		protected JungToSDBidiConverter(DirectedGraph<Vertex, Edge> origJungGraph) {
			jungGraph = origJungGraph;
		}
		
		protected TreeGraphNode getNode(Vertex v) {
			TreeGraphNode sdNode = sdNodes.get(v);
			if (sdNode == null) {
				sdNode = convertNode(v);
				sdNodes.put(v, sdNode);
				originalVerticesByIndex.put(v.getTokenPosition(), v);
			}
			return sdNode;
		}

		private TreeGraphNode convertNode(Vertex v) {
			CoreLabel label = new CoreLabel();
			label.setValue(v.getWord());
			label.setIndex(v.getTokenPosition());
			label.setWord(v.getWord());
			label.setLemma(v.getLemma());
			LOG.trace("Graph node label: {}", label);
			TreeGraphNode newNode = new TreeGraphNode(label);
			CoreLabel posLabel = new CoreLabel();
			posLabel.setValue(v.getPOSTag());
			newNode.setParent(new TreeGraphNode(posLabel));
			return newNode;
		}

		public DirectedGraph<Vertex, Edge> reconvertToJung(Collection<TypedDependency> sdDeps) {
			DirectedGraph<Vertex, Edge> converted = new DirectedSparseGraph<Vertex, Edge>();
			for (TypedDependency tDep : sdDeps) {
				Vertex gov = originalVerticesByIndex.get(tDep.gov().label().index());
				Vertex dep = originalVerticesByIndex.get(tDep.dep().label().index());
				LOG.trace("Mapping original gov {} to {} and dep {} to {} with label {}", 
						tDep.gov(), gov, tDep.dep(), dep, tDep.reln().getShortName());
				String label = tDep.reln().getShortName();
				String suff = tDep.reln().getSpecific();
				if (suff != null)
					label += "_" + suff;
				if (POSSIBLE_REMAPPED_LABELS.contains(label)){
					// could be a substitute to keep SD happy
					Edge oldEdge = jungGraph.findEdge(gov, dep);
					if (oldEdge != null)
						label = oldEdge.getLabel(); // replace it with the original
				}
				converted.addEdge(new Edge(gov, label, dep), gov, dep);
			}
			return converted;
		}
		
		public Pair<TreeGraphNode, List<TypedDependency>> getNativeStanfordDeps() {
			List<TypedDependency> typedDeps = new ArrayList<TypedDependency>();
			TreeGraphNode rootNode = null;
			for (Edge e : jungGraph.getEdges()) {
				if (e.getLabel().equals("root")) {
					if (rootNode != null) {
						if (LOG.isInfoEnabled())
							LOG.info("Multiple root nodes: {} and {}; using first",
									rootNode, getNode(e.getGovernor()));
						continue;
					}
					rootNode = getNode(e.getGovernor());
					LOG.trace("Set root node to {}", rootNode);
					continue;
				}
				String sdMappedLabel = CLEAR_TO_SD_LABELS.get(e.getLabel());
				String label = sdMappedLabel != null ? sdMappedLabel : e.getLabel();
				GrammaticalRelation gr = EnglishGrammaticalRelations.valueOf(label);
				if (gr == null) {
					LOG.trace("No known reln for '{}'; defaulting to dep", e.getLabel());
					gr = EnglishGrammaticalRelations.valueOf("dep"); // clearnlp has deps which SD doesn't
				}
				TreeGraphNode gov = getNode(e.getGovernor());
				TreeGraphNode dep = getNode(e.getDependent());
				TypedDependency tDep = new TypedDependency(gr, gov, dep);
				typedDeps.add(tDep);
			}
			if (rootNode == null) { // none found 
				int lowestAnyIndex = jungGraph.getVertexCount() + 1; // max poss value
				int lowestVerbIndex = lowestAnyIndex;
				TreeGraphNode fallbackRoot = null; // in case there are no verb nodes
				//heuristically attempt to use the first verb node:
				for (Vertex v : jungGraph.getVertices()) {
					if (v.getPOSTag().startsWith("VB") && v.getTokenPosition() < lowestVerbIndex) {
						rootNode = getNode(v);
						lowestVerbIndex = v.getTokenPosition();
					}
					if (v.getTokenPosition() < lowestAnyIndex) {
						lowestAnyIndex = v.getTokenPosition();
						fallbackRoot = getNode(v);
					}
				}
				if (rootNode == null) {
					LOG.info("No explicit root or verb node found; select first node {}",
							fallbackRoot);
					rootNode = fallbackRoot;
				} else {
					LOG.info("No root node found; selected first verb node {} instead", rootNode);
				}
			}
			LOG.debug("SD Typed dependencies are: {}; root node is: {}", typedDeps, rootNode);
			return new Pair<TreeGraphNode, List<TypedDependency>>(rootNode, typedDeps);
		}

	}
	
	protected static class WordWithJungNode extends Word {
		Vertex vert;
		protected WordWithJungNode(Vertex v) {
			super(v.getToken());
			vert = v;
		}
	}
}
