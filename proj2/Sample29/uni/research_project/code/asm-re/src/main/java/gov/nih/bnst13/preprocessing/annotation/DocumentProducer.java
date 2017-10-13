package gov.nih.bnst13.preprocessing.annotation;

import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;

import java.util.List;
import java.util.Map;

import com.nicta.biomed.bnst13.annotations.AnnotatedDocument;

public interface DocumentProducer {
	
	/**
	 * retrieve fully annotated documents combined with dependency graphs
	 * @return documents
	 */
	public Map<String, ? extends List<? extends AnnotatedSentence>> getIdsToAnnotatedSentences();
	
	/**
	 * retrieve last protein ID of all documents
	 * @return lastProteinIDOfEachDocument
	 */
	public Map<String, Integer> getLastProteinIDOfDocuments();

	/** Return an Iterable over all of the documents in the collection
	 * 
	 * (implementing classes should feel free to read directly off
	 * disk instead of loading into memory to reduce memory requirements */
	public Iterable<AnnotatedDocument> documents();
}
