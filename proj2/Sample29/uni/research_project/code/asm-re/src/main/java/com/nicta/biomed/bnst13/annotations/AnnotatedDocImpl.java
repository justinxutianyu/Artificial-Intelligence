package com.nicta.biomed.bnst13.annotations;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public abstract class AnnotatedDocImpl implements AnnotatedDocument {

	protected List<BnstTermAnnotation> termAnns = new ArrayList<BnstTermAnnotation>();
	protected List<BnstEventAnnotation> evtAnns = new ArrayList<BnstEventAnnotation>();
	protected boolean isTraining;
	private int lastProteinId;
	private String docId = "";

	AnnotatedDocImpl(String docId, boolean isTraining) {
		this.docId = docId;
		this.isTraining = isTraining;
	}

	AnnotatedDocImpl(String docId) {
		this(docId, true);
	}

	public AnnotatedDocImpl() {
		this("");
	}

	/**
	 * Initialize the list of annotations - should be called in subclass
	 * constructors
	 */
	protected void init() throws IOException {
		if (isTraining) {
			readAllTermAnns();
			readEventAnns();
		} else {
			readProteinAnns();
		}
	}

	protected abstract String eventFile();

	protected abstract String entityFile();

	protected void readEventAnns() throws IOException {
		evtAnns.addAll(BnstEventAnnotation.readFile(eventFile()));
	}

	private void readProteinAnns() throws IOException {
		termAnns.addAll(BnstTermAnnotation.readFile(entityFile()));
		if (termAnns.size() == 0) {
			lastProteinId = -1 ;
			return;
		}
		String lastProtStringId = termAnns.get(termAnns.size() - 1).getId();
		String lastProtNum = lastProtStringId.substring(BnstTermAnnotation.TERM_PREFIX
				.length());
		lastProteinId = Integer.parseInt(lastProtNum);
	}

	protected void readAllTermAnns() throws IOException {
		readProteinAnns();
		termAnns.addAll(BnstTermAnnotation.readFile(eventFile(), true));
	}

	public int getLastProteinId() {
		return lastProteinId;
	}

	@Override
	public String getId() {
		return docId;
	}

	public void setId(String docId) {
		this.docId = docId;
	}

}
