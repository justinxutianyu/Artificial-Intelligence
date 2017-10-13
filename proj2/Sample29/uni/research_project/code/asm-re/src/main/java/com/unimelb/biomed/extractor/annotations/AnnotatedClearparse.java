package com.unimelb.biomed.extractor.annotations;

import gov.nih.bnst.preprocessing.annotation.Argument;
import gov.nih.bnst.preprocessing.annotation.Event;
import gov.nih.bnst.preprocessing.annotation.Protein;
import gov.nih.bnst.preprocessing.annotation.Relation;
import gov.nih.bnst.preprocessing.annotation.Trigger;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.dp.DependencyGraph;
import gov.nih.bnst.preprocessing.dp.Vertex;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.dependency.DEPNode;
import com.googlecode.clearnlp.dependency.DEPTree;
import com.googlecode.clearnlp.util.Span;
import com.unimelb.biomed.extractor.RangeIndexer;
import com.unimelb.biomed.extractor.SpanBoundsIndexer;
import com.unimelb.biomed.extractor.learning.GenAnnotatedSentence;
import com.unimelb.biomed.extractor.standeps.SDLikeDepGraph;
import com.unimelb.biomed.extractor.textprocess.GraphTransformer;
import com.unimelb.biomed.extractor.textprocess.TransformedDependencyGraph;

public class AnnotatedClearparse {
	private static final Logger LOG = LoggerFactory.getLogger(AnnotatedClearparse.class);

	private DEPTree tree;
	private Span sentenceSpan;
	private List<BnstTermAnnotation> termAnnotations = new ArrayList<BnstTermAnnotation>();
	private List<List<Integer>> termAnnNodeIndexes = new ArrayList<List<Integer>>();
	private Set<String> termAnnotationIds = new HashSet<String>();

    private Set<String> eventAnnotationIds = new HashSet<String>();
	private List<BnstEventAnnotation> eventAnnotations = new ArrayList<BnstEventAnnotation>();

    private Set<String> relationshipAnnotationIds = new HashSet<String>();
	private List<BnstRelationAnnotation> relationshipAnnotations = new ArrayList<BnstRelationAnnotation>();

    private int sentenceId;

	private SpanBoundsIndexer<Integer> spanIndexer = new SpanBoundsIndexer<Integer>();

	private SDLikeDepGraph sdt;

	private DependencyGraph transformedGraph = null;

	private GraphTransformer graphTransformer = null;

	public AnnotatedClearparse(DEPTree tree, List<BnstTermAnnotation> termAnns,
			int sentId) {
		this(
            tree,
            termAnns,
            new ArrayList<BnstEventAnnotation>(),
            new ArrayList<BnstRelationAnnotation>(),
            sentId
        );
	}

	public AnnotatedClearparse(DEPTree tree, List<BnstTermAnnotation> termAnns,
			List<BnstEventAnnotation> eventAnns, List<BnstRelationAnnotation> relAnns, int sentId) {
		//LOG.debug("Getting annotated ClearParser parse for {}", sentId);
		this.tree = tree;
		sdt = new SDLikeDepGraph(this.tree);
		sentenceSpan = new Span();
		for (DEPNode node : tree) {
			if (!node.span.hasValues())
				continue;
			if (sentenceSpan.begin == Span.UNKNOWN || node.span.begin < sentenceSpan.begin)
				sentenceSpan.begin = node.span.begin;
			if (sentenceSpan.end == Span.UNKNOWN || node.span.end > sentenceSpan.end)
				sentenceSpan.end = node.span.end;
		}
		indexTreeBySpan();
		readTermAnnotations(termAnns);
		readDirectEventAnnotations(eventAnns);
		readNestedEventAnnotations(eventAnns);
        readRelationAnnotations(relAnns);
        postProcessRelationAnnotations();
        sentenceId = sentId;
	}

	public void setTransformer(GraphTransformer transformer) {
		transformedGraph = new TransformedDependencyGraph(sdt, transformer);
	}

	public AnnotatedClearparse(DEPTree tree, List<BnstTermAnnotation> termAnns,
			List<BnstEventAnnotation> eventAnns) {
		this(
            tree,
            termAnns,
            eventAnns,
            new ArrayList<BnstRelationAnnotation>(),
             -1
        );
	}

	protected class CPAnnotatedSentence extends GenAnnotatedSentence {

		public CPAnnotatedSentence() {
			super(sentenceId);
		}

		@Override
		public DependencyGraph getDependencyGraph() {
			return transformedGraph != null ? transformedGraph : sdt;
		}

		@Override
		public int getStartIndex() {
			return sentenceSpan.begin;
		}

		@Override
		public int getEndIndex() {
			return sentenceSpan.end;
		}
	}


	public AnnotatedSentence getAnnSentence(String corpus) {

        CPAnnotatedSentence annSent = new CPAnnotatedSentence();

        //Sentences derived from the Genia corpus will have a set
        //of proteins and triggers.
        Map<String, Protein> proteins = new HashMap<String, Protein>();
        Map<String, Trigger> triggers = new HashMap<String, Trigger>();

        //Sentences derived from other corpora will simply have a
        //set of arguments.
        Map<String, Argument> arguments = new HashMap<String, Argument>();

        //For Genia corpus, classify term annotations as either a
        //protein or a trigger.
        if (corpus.equals("genia")) {
            int idx = 0;
    		for (BnstTermAnnotation ta : termAnnotations) {
    			Set<Vertex> vertices = new HashSet<Vertex>();
    			for (Integer nodeIdx : termAnnNodeIndexes.get(idx))
    				vertices.add(sdt.getVertex(nodeIdx));
    			LOG.trace("Found {}trigger vertices: {}",
    					ta.isTrigger() ? "" : "non-", vertices);
    			if (ta.isTrigger()) {
    				Trigger trig = ta.asTriggerInstance();
    				trig.setTriggerNodes(vertices);
    				trig.setTriggerCenterNode(annSent.findCenterNode(vertices));
    				triggers.put(trig.getTriggerID(), trig);
    			} else {
    				Protein prot = ta.asProteinInstance();
    				proteins.put(prot.getProteinID(), prot);
    			}
    			idx++;
    		}
    		annSent.setProteins(proteins);
    		annSent.postprocessProteinNodes();
    		annSent.setTriggers(triggers);
        }
        //For other corpora, store each term annotation as generic arguments
        else {
            int idx = 0;
            for (BnstTermAnnotation ta : termAnnotations) {
                LOG.info("Doing term annotation {}", ta.getId());
                List<Vertex> vertices = new ArrayList<Vertex>();

                for (Integer nodeIdx : termAnnNodeIndexes.get(idx)) {
                    LOG.info("Vertex with arg ID {} is associated", sdt.getVertex(nodeIdx).getArgumentID());
    				vertices.add(sdt.getVertex(nodeIdx));
                }
                LOG.warn(
                    "Found {} dependency graph nodes corresponding "
                    + "to annotation {}. Only the first node retrieved "
                    + "will be used", vertices.size(), ta.getId()
                );

                Argument arg = ta.asArgumentInstance();
                arg.setGraphNode(vertices.get(0));
                arguments.put(arg.getArgumentID(), arg);
                LOG.debug("Added argument {} with ID {}", arg, arg.getArgumentID());

    			idx++;
    		}
            //annSent.postprocessArgumentNodes();
            annSent.setArguments(arguments);
        }

        //For variome corpus, we parse relationship annotations
        if (corpus.equals("variome")) {
            Map<String, Relation> relationships = new HashMap<String, Relation>();
    		for (BnstRelationAnnotation ra : relationshipAnnotations) {
                //Check that each argument of the sentence exists in the
                //maps we built up above.
                for (String termId : ra.getArgIds()) {
                    if (termId.startsWith(BnstTermAnnotation.TERM_PREFIX)
                        && !arguments.containsKey(termId))
                            throw new BnstRuntimeException("Term " + termId +
                                " is outside sentence boundaries in relationship " + ra.getId());
    			}
    			LOG.debug("Outputting relationship {}", ra);
                Relation rel;
                rel = ra.asRelationInstance();
                relationships.put(rel.getRelationID(), rel);
    		}
    		annSent.setRelations(relationships);
        }
        //For other corpora, we parse event annotations
        else {
            Map<String, Event> events = new HashMap<String, Event>();
    		for (BnstEventAnnotation ea : eventAnnotations) {
                //Check that each argument of the sentence exists in the
                //maps we built up above.
                for (String termId : ea.getTriggerAndArgIds()) {
                    //For Genia we want the argument to exist as either a
                    //trigger or a protein
                    if (corpus.equals("genia")) {
                        if (termId.startsWith(BnstTermAnnotation.TERM_PREFIX)
                            && !proteins.containsKey(termId)
                            && !triggers.containsKey(termId))
                                throw new BnstRuntimeException("Term " + termId +
                                    " is outside sentence boundaries in event " + ea.getId());
                    }
                    //For other corpora we want the argument to exist as
                    //an argument.
                    else {
                        if (termId.startsWith(BnstTermAnnotation.TERM_PREFIX)
                            && !arguments.containsKey(termId))
                                throw new BnstRuntimeException("Term " + termId +
                                    " is outside sentence boundaries in event " + ea.getId());
                    }
    			}
    			LOG.trace("Outputting event {}", ea);
                Event ev;
                if (corpus.equals("genia"))
                    ev = ea.asEventInstance();
                else
                    ev = ea.asThemeEventInstance();
                events.put(ev.getEventID(), ev);
    		}
    		annSent.setEvents(events);
        }
		return annSent;
	}

	private void indexTreeBySpan() {
		for (int i = 0; i < tree.size(); i++)
			spanIndexer.index(tree.get(i).span, i);
	}

	/**
	 * Get P+A+P file in the format required by Haibin
	 *
	 * @return
	 */
	public String getPAP() {
		StringBuilder builder = new StringBuilder();
		builder.append(sdt.toString());
		for (int i = 0; i < termAnnotations.size(); i++) {
			builder.append(termAnnotations.get(i));
			builder.append("\t");
			// get the list of nodes corresponding to the annotation
			List<Integer> nodeIndexes = termAnnNodeIndexes.get(i);
			boolean isFirstNode = true;
			for (Integer nodeIdx : nodeIndexes) {
				if (!isFirstNode)
					builder.append(" ");
				builder.append(sdt.getNode(nodeIdx).toString());
				isFirstNode = false;
			}
			builder.append("\n");
		}
		for (BnstEventAnnotation ann : eventAnnotations) {
			builder.append(ann.toString());
			builder.append("\n");
		}
		return builder.toString();
	}

	private void readTermAnnotations(List<BnstTermAnnotation> anns) {
		for (BnstTermAnnotation ann : anns)
			readTermAnnotation(ann);
	}

	private void readTermAnnotation(BnstTermAnnotation ann) {
		LOG.trace("Checking annotation {}", ann);
		Span span = ann.getSpan();
		if (span.end < sentenceSpan.begin || span.begin >= sentenceSpan.end) {
			LOG.trace("Annotation span {} is outside sentence at {}; not examining", span,
					sentenceSpan);
			return;
		}
		List<Integer> overlaps = spanIndexer.overlaps(span);
		if (overlaps.isEmpty()) {
			LOG.warn("No tokens found within span {}", span);
			return;
		}
		LOG.trace("Matched bio-entity span {} to POS nodes {}", span,
			overlaps);
		DEPNode firstNode = tree.get(overlaps.get(0));
		DEPNode lastNode = tree.get(overlaps.get(overlaps.size() - 1));
		int startMismatch = span.begin - firstNode.span.begin;
		int endMismatch = span.end - lastNode.span.end;
		if ((startMismatch > 0 || endMismatch > 0)) {
			boolean isMinor = startMismatch == 1 && endMismatch == 1;
			if (!isMinor || LOG.isInfoEnabled()) {
				String annKind = ann.isTrigger() ? "Trigger" : "Bio-entity";
				LOG.warn("Range mismatch for {} span {} with Dep node {} at {}", annKind, span,
						firstNode, firstNode.span);
				if (firstNode != lastNode)
					LOG.warn("(End of span is {} at {}", lastNode, lastNode.span);
			}
		}
		ArrayList<Integer> nodeIndexes = new ArrayList<Integer>();
		for (Integer i : overlaps)
			nodeIndexes.add(i);
		termAnnNodeIndexes.add(nodeIndexes);
		termAnnotations.add(ann);
		termAnnotationIds.add(ann.getId());
		LOG.trace("Now have {} active annotations", termAnnotations.size());
	}

	private void readDirectEventAnnotations(List<BnstEventAnnotation> eventAnns) {
		for (BnstEventAnnotation eventAnn : eventAnns) {
			LOG.trace("considering event annotation {} (as direct)", eventAnn);
			if (!referencesExternalTerms(eventAnn)
					&& !referencesEvents(eventAnn)) {
				eventAnnotationIds.add(eventAnn.getId());
				eventAnnotations.add(eventAnn);
				LOG.trace("Adding event annotation {}", eventAnn);
			}
		}
	}

    private void readRelationAnnotations(List<BnstRelationAnnotation> relationshipAnns) {
        for (BnstRelationAnnotation relationshipAnn : relationshipAnns) {
			LOG.debug("considering relationship annotation {}", relationshipAnn);
            if (!referencesExternalTerms(relationshipAnn)) {
                relationshipAnnotationIds.add(relationshipAnn.getId());
			    relationshipAnnotations.add(relationshipAnn);
			    LOG.debug("Adding relationship annotation {} for sentence {}", relationshipAnn, sentenceId);
            }
        }
    }

    private void postProcessRelationAnnotations() {
        for (BnstRelationAnnotation relation : this.relationshipAnnotations) {
            //Get the relationType
            String relationType = relation.getRelationType();
            //Look up the name of each argument
            ArrayList<String> argNames = new ArrayList<String>();
            for (String argId : relation.getArgIds()) {
                for (BnstTermAnnotation termAnn : termAnnotations) {
                    if (argId.equals(termAnn.getId())) {
                        argNames.add(termAnn.getName().replace("-", "").replace("_", "").toLowerCase());
                    }
                }
            }
            //Reset relationType as arg1Name + relationType + arg2Name.toLower()
            Collections.sort(argNames);
            relation.setRelationType(
                (argNames.get(0) +
                relationType +
                argNames.get(1)).replace("-", "").replace("_", "").toLowerCase()
            );
        }
    }

	private boolean referencesExternalTerms(BnstEventAnnotation eventAnn) {
		for (String id : eventAnn.getTriggerAndArgIds()) {
			if (!id.startsWith(BnstTermAnnotation.TERM_PREFIX)) // ignore complex args here
				continue;
			if (!termAnnotationIds.contains(id)) {
				LOG.trace("Term {} is external to sentence at {} for {}",
						id, sentenceSpan, eventAnn.getId());
				return true;
			}
		}
		return false;
	}

    private boolean referencesExternalTerms(BnstRelationAnnotation relationshipAnn) {
		for (String id : relationshipAnn.getArgIds()) {
			if (!id.startsWith(BnstTermAnnotation.TERM_PREFIX)) // ignore complex args here
				continue;
			if (!termAnnotationIds.contains(id)) {
				LOG.trace("Term {} is external to sentence at {} for {}",
						id, sentenceSpan, relationshipAnn.getId());
				return true;
			}
		}
		return false;
	}

	private boolean referencesEvents(BnstEventAnnotation eventAnn) {
		for (String id : eventAnn.getTriggerAndArgIds()) {
			if (!id.startsWith(BnstTermAnnotation.TERM_PREFIX))
				return true;
		}
		return false;
	}

	private void readNestedEventAnnotations(List<BnstEventAnnotation> eventAnns) {
		// here we read in events which have other relevant events as arguments
		boolean added = true;
		while (added) { // keep reading while new ones are added -- we need the
			// transitive closure
			added = false;
			for (BnstEventAnnotation eventAnn : eventAnns) {
				LOG.trace("Considering event annotation {} (as nested)", eventAnn);
				LOG.trace("Known term Ids: {}; event IDs: {}", termAnnotationIds,
						eventAnnotationIds);
				if (!referencesEvents(eventAnn))
					continue;
				if (referencesExternalTerms(eventAnn)) {
					LOG.trace("{} references external terms -- ignoring", eventAnn);
					continue;
				}
				if (eventAnnotationIds.contains(eventAnn.getId())) {
					LOG.trace("{} is already added -- ignoring", eventAnn);
					continue;
				}
				boolean argsAreWithin = true;
				for (String argId : eventAnn.getTriggerAndArgIds()) {
					// if we're here we know:
					//  a) any protein/trigger arguments are within the sentence
					//  b) the arguments reference one *or more* events
					// so we need to check only event arguments,
					// to make sure they are ones we already konw about
					// for this sentence
					if (!argId.startsWith(BnstTermAnnotation.TERM_PREFIX)) {
						if (!eventAnnotationIds.contains(argId)) {
							argsAreWithin = false;
							LOG.trace("Do not know about event argument {} -- not adding {}",
									argId, eventAnn);
							break;
						} else {
							LOG.trace(
									"Still considering event annotation {} as event {} is already known",
									eventAnn, argId);
						}
					}
				}
				if (argsAreWithin) {
					LOG.trace("Added event (with nested arguments) {}", eventAnn);
					added = true;
					eventAnnotationIds.add(eventAnn.getId());
					eventAnnotations.add(eventAnn);
					break;
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
}
