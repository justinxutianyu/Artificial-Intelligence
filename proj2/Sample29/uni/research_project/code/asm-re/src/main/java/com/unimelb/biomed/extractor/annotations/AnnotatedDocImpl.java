package com.unimelb.biomed.extractor.annotations;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public abstract class AnnotatedDocImpl implements AnnotatedDocument {

	protected List<BnstTermAnnotation> termAnns = new ArrayList<BnstTermAnnotation>();
	protected List<BnstEventAnnotation> evtAnns = new ArrayList<BnstEventAnnotation>();
    protected List<BnstRelationAnnotation> relAnns = new ArrayList<BnstRelationAnnotation>();
	protected boolean isTraining;
	private int lastProteinId;
	private String docId = "";
    protected String corpus;

    public AnnotatedDocImpl(String docId, String corpus, boolean isTraining) {
		this.docId = docId;
		this.isTraining = isTraining;
        this.corpus = corpus;
	}

	public AnnotatedDocImpl(String docId, boolean isTraining) {
        this(docId, "", isTraining);
	}

	public AnnotatedDocImpl(String docId) {
		this(docId, true);
	}

	public AnnotatedDocImpl() {
		this("");
	}

    public List<BnstTermAnnotation> getTermAnnotations() {
        return termAnns;
    }

    public List<BnstEventAnnotation> getEvtAnnotations() {
        return evtAnns;
    }

    public List<BnstRelationAnnotation> getRelationAnnotations() {
        return relAnns;
    }


	/**
	 * Initialize the list of annotations - should be called in subclass
	 * constructors
	 */
	protected void init() throws IOException {
        //If we're not dealing with variome, read in events
        if (isTraining && !corpus.equals("variome")) {
			readAllTermAnns();
			readEventAnns();
        //If we are dealing with variome, read relations
        } else if (corpus.equals("variome")) {
            readAllTermAnns();
            readRelationAnns();
        } else {
            //Don't know why we insist on reading these in
            //Non-training data.
            if (corpus.equals("genia"))
                readProteinAnns();
		}
	}

	protected abstract String eventFile();

	protected abstract String entityFile();

	protected void readEventAnns() throws IOException {
		evtAnns.addAll(BnstEventAnnotation.readFile(eventFile(), corpus));
	}

    protected void readRelationAnns() throws IOException {
		relAnns.addAll(BnstRelationAnnotation.readFile(eventFile()));
	}

	private void readProteinAnns() throws IOException {
		termAnns.addAll(BnstTermAnnotation.readFile(entityFile(), corpus));
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
        if (!corpus.equals("variome")) {
            readProteinAnns();
		    termAnns.addAll(BnstTermAnnotation.readFile(entityFile(), corpus, true));
            termAnns.addAll(BnstTermAnnotation.readFile(eventFile(), corpus, true));
        } else {
            termAnns.addAll(BnstTermAnnotation.readFile(eventFile(), corpus, true));
        }
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

    @Override
    public String getCorpus() {
        return corpus;
    }

    public void setCorpus() {
        this.corpus = corpus;
    }

}
