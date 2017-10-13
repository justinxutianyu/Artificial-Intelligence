package com.nicta.biomed.bnst13.annotations;

import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import gov.nih.bnst13.preprocessing.annotation.DocumentProducer;
import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;

public abstract class AnnotatedDocCollection implements DocumentProducer {

	Map<String, AnnotatedDocument> annDocs = new HashMap<String, AnnotatedDocument>();
	
	public AnnotatedDocCollection() {
	}
	
	public void addDoc(AnnotatedDocument doc) {
		annDocs.put(doc.getId(), doc);
	}
	
	@Override
	public Map<String, ? extends List<? extends AnnotatedSentence>> getIdsToAnnotatedSentences() {
		Map<String, List<? extends AnnotatedSentence>> annSents = 
				new HashMap<String, List<? extends AnnotatedSentence>>();
		for (Map.Entry<String, AnnotatedDocument> docEntry : annDocs.entrySet()) 
			annSents.put(docEntry.getKey(), docEntry.getValue().getAnnSentences());
		return annSents;
	}

	@Override
	public Map<String, Integer> getLastProteinIDOfDocuments() {
		Map<String, Integer> lastPids = new HashMap<String, Integer>();
		for (Map.Entry<String, AnnotatedDocument> docEntry : annDocs.entrySet()) {
			int protId = docEntry.getValue().getLastProteinId();
			if (protId != -1) 
				lastPids.put(docEntry.getKey(), protId);
		}
		return lastPids;
	}

	/** Return an Iterable over all of the documents in the collection
	 * 
	 * (implementing classes should feel free to read directly off
	 * disk instead of loading into memory to reduce memory requirements */
	public abstract Iterable<AnnotatedDocument> documents();
}
