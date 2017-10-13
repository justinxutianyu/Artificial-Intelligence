package com.unimelb.biomed.extractor.annotations;

import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;

import java.util.Iterator;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.SharedTaskHelper;
import com.unimelb.biomed.extractor.textprocess.GraphTransformer;

public class AnnotatedCPDocsFromDirectory extends AnnotatedDocCollection {
	private static final Logger LOG = LoggerFactory.getLogger(AnnotatedCPDocsFromDirectory.class);

	private final String annotationsDir;
	private final String parseDir;
    private final String corpus;
	private GraphTransformer graphTransformer = null;

	private boolean forTraining;

	public Map<String, ? extends List<? extends AnnotatedSentence>> getIdsToAnnotatedSentences() {
		for (AnnotatedDocument doc : documents())
			addDoc(doc);
		return super.getIdsToAnnotatedSentences();
	}

	public AnnotatedCPDocsFromDirectory(String parseDir, String annotationsDir, String corpus, boolean forTraining) {
		this.annotationsDir = annotationsDir;
		this.parseDir = parseDir;
        this.corpus = corpus;
		this.forTraining = forTraining;
	}

    public AnnotatedCPDocsFromDirectory(String parseDir, String annotationsDir, boolean forTraining) {
		this.annotationsDir = annotationsDir;
		this.parseDir = parseDir;
        this.corpus = "";
		this.forTraining = forTraining;
	}

	public AnnotatedCPDocsFromDirectory(String parseDir, String annotationsDir) {
		this(parseDir, annotationsDir, true);
	}

	public void setGraphTransformer(GraphTransformer graphTransformer) {
		this.graphTransformer = graphTransformer;
	}

	private AnnotatedDocument getAnnotatedDoc(String parseFile, String corpus) {
		try {
            AnnotatedCPDoc cpd = new AnnotatedCPDoc(parseFile, annotationsDir, corpus, forTraining);
			if (graphTransformer != null)
				cpd.setGraphTransformer(graphTransformer);
			return cpd;
		} catch (IOException e) {
			throw new BnstRuntimeException(e);
		}
	}

    private AnnotatedDocument getAnnotatedDoc(String parseFile) {
		try {
			AnnotatedCPDoc cpd = new AnnotatedCPDoc(parseFile, annotationsDir, corpus, forTraining);
			if (graphTransformer != null)
				cpd.setGraphTransformer(graphTransformer);
			return cpd;
		} catch (IOException e) {
			throw new BnstRuntimeException(e);
		}
	}

	public Iterable<AnnotatedDocument> documents() {
		return new DocIterable();
	}

	protected class DocIterable implements Iterable<AnnotatedDocument> {
		@Override
		public Iterator<AnnotatedDocument> iterator() {
			return new DocIterator();
		}
	}

	protected class DocIterator implements Iterator<AnnotatedDocument> {
		private int i = 0;

		private File[] fileList = null;

		public DocIterator() {
			File dir = new File(parseDir);
			fileList = dir.listFiles(new ParsedFileFilter());
		}

		@Override
		public boolean hasNext() {
			if (fileList == null || !(i < fileList.length))
				return false;
			return true;
		}

		@Override
		public AnnotatedDocument next() {
			AnnotatedDocument doc = getAnnotatedDoc(fileList[i].getAbsolutePath(), corpus);
			i++;
			return doc;
		}

		@Override
		public void remove() {
			throw new UnsupportedOperationException();
		}
	}


}

class ParsedFileFilter implements FileFilter {
	@Override
	public boolean accept(File pathname) {
		return pathname.getName().endsWith(SharedTaskHelper.PARSED_SUFFIX);
	}

}
