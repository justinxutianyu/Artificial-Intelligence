package com.unimelb.biomed.extractor.textprocess;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.feature.xml.POSFtrXml;
import com.googlecode.clearnlp.pos.POSNode;
import com.googlecode.clearnlp.pos.POSTagger;
import com.googlecode.clearnlp.util.Span;
import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;
import com.unimelb.biomed.extractor.RangeIndexer;
import com.unimelb.biomed.extractor.SpanBoundsIndexer;

public class BnstPosTagger extends POSTagger {
	private static final Logger LOG = LoggerFactory
			.getLogger(BnstPosTagger.class);

    /** naive bio entities, store only map from span -> string */
	private SortedMap<Span, String> naiveBioEntities =
        new TreeMap<Span, String>(new SpanComparator());

    /** full bio entities, store full annotation */
    private SortedMap<Span, BnstBioEntity> bioEntities =
        new TreeMap<Span, BnstBioEntity>(new SpanComparator());

	/** the string used to tag bio-entities marked in shared task data */
	private static final String BIO_ENTITY_FORM = "BIO_Entity";
	/** the POS tag for bio entities */
	private static final String BIO_ENTITY_POS = "NNP";
    /** prefix used for relation arguments */
    private static final String ARG_PREFIX = "ARG_";


	@Override
	public void init(List<POSNode> nodes) {
		super.init(nodes);
	}

	@Override
	public void tag(List<POSNode> nodes) {
		super.tag(nodes);
		SpanBoundsIndexer<Integer> spanIndexer = new SpanBoundsIndexer<Integer>();
		int sentenceBeginIdx = nodes.get(0).span.begin;
		int sentenceEndIdx = nodes.get(nodes.size() - 1).span.end;
		for (int i = 0; i < nodes.size(); i++) {
			POSNode node = nodes.get(i);
			LOG.trace("Indexing POS node '{}' ({}) at span {}", node, i, node.span);
			spanIndexer.index(node.span, i);
		}
		Set<Integer> nodeIndexesForRemoval = new HashSet<Integer>();
		int beIndex = 0;
        if (!naiveBioEntities.isEmpty()) {
    		for (Map.Entry<Span, String> spanIdEntry : naiveBioEntities.entrySet()) {
    			Span beSpan = spanIdEntry.getKey();
    			String entId = spanIdEntry.getValue();
    			if (sentenceEndIdx < beSpan.begin || sentenceBeginIdx > beSpan.end) {
    				LOG.trace(
                        "Sentence at {}:{} has no overlaps " +
                        "with entity at {}; skipping",
    					sentenceBeginIdx,
                        sentenceEndIdx,
                        beSpan
                    );
    				continue;
    			}
    			List<Integer> overlaps = spanIndexer.overlaps(beSpan);
    			if (overlaps.isEmpty()) {
    				LOG.warn("No tokens found within span {}", beSpan);
    				continue;
    			}
    			LOG.trace("Matched bio-entity span {} to POS nodes {}", beSpan,
    					overlaps);
    			int first = overlaps.get(0);
    			int last = overlaps.get(overlaps.size() - 1);
    			POSNode firstNode = nodes.get(first);
    			POSNode lastNode = nodes.get(last);
    			if (firstNode.span.begin != beSpan.begin)
    				LOG.warn(
    						"Start range mismatch for Bio-entity span {} with POS node {} at {}",
    						beSpan, firstNode, firstNode.span);
    			if (nodes.get(last).span.end != beSpan.end)
    				LOG.warn(
    						"End range mismatch for Bio-entity span {} with POS node {} at {}",
    						beSpan, lastNode, lastNode.span);
    			if (overlaps.size() > 1) {
    				firstNode.span.end = lastNode.span.end;
    				for (int nodeIdx : overlaps.subList(1, overlaps.size()))
    					nodeIndexesForRemoval.add(nodeIdx);
    			}
    			firstNode.form = BIO_ENTITY_FORM + entId;
    			firstNode.pos = BIO_ENTITY_POS;
    		}
        }
        else {
            for (Map.Entry<Span, BnstBioEntity> entry : bioEntities.entrySet()) {
    			Span beSpan = entry.getKey();
    			BnstBioEntity entity = entry.getValue();
    			if (sentenceEndIdx < beSpan.begin || sentenceBeginIdx > beSpan.end) {
    				LOG.info(
                        "Sentence at {}:{} has no overlaps " +
                        "with entity at {}; skipping",
    					sentenceBeginIdx,
                        sentenceEndIdx,
                        beSpan
                    );
    				continue;
    			}
    			List<Integer> overlaps = spanIndexer.overlaps(beSpan);
    			if (overlaps.isEmpty()) {
    				LOG.warn("No tokens found within span {}", beSpan);
    				continue;
    			}
    			LOG.info(
                    "Matched bio-entity span {} to POS nodes {}",
                    beSpan,
    				overlaps
                );
    			int first = overlaps.get(0);
    			int last = overlaps.get(overlaps.size() - 1);
    			POSNode firstNode = nodes.get(first);
    			POSNode lastNode = nodes.get(last);
    			if (firstNode.span.begin != beSpan.begin)
    				LOG.warn(
						"Start range mismatch for Bio-entity " +
                        "span {} with POS node {} at {}",
						beSpan, firstNode, firstNode.span);
    			if (nodes.get(last).span.end != beSpan.end)
    				LOG.warn(
						"End range mismatch for Bio-entity " +
                        "span {} with POS node {} at {}",
						beSpan, lastNode, lastNode.span);
    			if (overlaps.size() > 1) {
    				firstNode.span.end = lastNode.span.end;
    				for (int nodeIdx : overlaps.subList(1, overlaps.size()))
    					nodeIndexesForRemoval.add(nodeIdx);
    			}
    			firstNode.form =
                    ARG_PREFIX
                    + entity.getEntityDescription().replace("-", "").toLowerCase()
                    + entity.getEntityID();
                firstNode.pos = BIO_ENTITY_POS;
    		}
        }
		if (!nodeIndexesForRemoval.isEmpty()) {
			// length changed due to multi-token NE
			List<POSNode> origNodes = new ArrayList<POSNode>(nodes);
			nodes.clear();
			for (int i = 0; i < origNodes.size(); i++) {
				if (nodeIndexesForRemoval.contains(i))
					continue;
				nodes.add(origNodes.get(i));
			}
		}
	}

	public void readGeniaBioEntities(InputStream fin) throws IOException {
		naiveBioEntities.clear();
		BufferedReader reader = new BufferedReader(new InputStreamReader(fin));
		String line;
		while ((line = reader.readLine()) != null) {
			String[] tabSepd = line.split("\t");
			String entIdString = tabSepd[0];
			String entId = entIdString.substring("T".length());
			String entityInfo = tabSepd[1];
			String[] entityComps = entityInfo.split(" ");
			int begin = Integer.parseInt(entityComps[1]);
			int end = Integer.parseInt(entityComps[2]);
			LOG.trace("Read new bio-entity at {}:{}", begin, end);
			naiveBioEntities.put(new Span(begin, end), entId);
		}
	}

    public void readVariomeBioEntities(InputStream fin) throws IOException {
		bioEntities.clear();
		BufferedReader reader = new BufferedReader(new InputStreamReader(fin));
		String line;
		while (((line = reader.readLine()) != null) && !(line.startsWith("R"))) {
			String[] tabSepd = line.split("\t");
			String entIdString = tabSepd[0];
			String entId = entIdString.substring("T".length());
			String entityInfo = tabSepd[1];
            String[] entityComps = entityInfo.split(" ");
            String entityDescription = entityComps[0];
            int begin = Integer.parseInt(entityComps[1]);
			int end = Integer.parseInt(entityComps[2]);

            Span entitySpan = new Span(begin, end);
            BnstBioEntity entity = new BnstBioEntity(
                entitySpan,
                entId,
                entityDescription,
                line
            );
            LOG.trace("Read new bio-entity at {}:{}", begin, end);
            bioEntities.put(entitySpan, entity);
		}
	}

    public void readSeeDevBioEntities(InputStream fin) throws IOException {
		naiveBioEntities.clear();
		BufferedReader reader = new BufferedReader(new InputStreamReader(fin));
		String line;
		while ((line = reader.readLine()) != null) {
			String[] tabSepd = line.split("\t");
			String entIdString = tabSepd[0];
			String entId = entIdString.substring("T".length());
			String entityInfo = tabSepd[1];
			String[] entityComps = entityInfo.split(" ");
            //TODO: Handle multiple spans in SeeDev theme annotations properly
			int begin = Integer.parseInt(entityComps[1]);
			int end = Integer.parseInt(entityComps[entityComps.length - 1]);
			LOG.trace("Read new bio-entity at {}:{}", begin, end);
            naiveBioEntities.put(new Span(begin, end), entId);
		}
	}

	public void readBioEntities(String entityFile, String corpus)
			throws FileNotFoundException, IOException {
		LOG.debug("Reading Bio entities from entity file {}", entityFile);
        if (corpus.equals("genia")) {
            readGeniaBioEntities(new FileInputStream(entityFile));
        }
        else if (corpus.equals("variome")) {
            readVariomeBioEntities(new FileInputStream(entityFile));
        }
        else if (corpus.equals("seedev")) {
            readSeeDevBioEntities(new FileInputStream(entityFile));
        }
        else {
            throw new BnstRuntimeException(
                "The "
                + corpus
                + " corpus is unsupported."
                + "Supported corpora are: genia, variome and seedev."
                + "Please see README.md for details on implementing new corpora."
            );
        }
	}

	public BnstPosTagger(POSFtrXml xml, BufferedReader fin) {
		super(xml, fin);
		LOG.debug("Initialized new BnstPosTagger instance");
	}

}
