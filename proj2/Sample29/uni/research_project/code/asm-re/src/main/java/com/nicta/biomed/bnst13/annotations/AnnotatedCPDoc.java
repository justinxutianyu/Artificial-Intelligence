package com.nicta.biomed.bnst13.annotations;

import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.dependency.DEPTree;
import com.googlecode.clearnlp.reader.JointReader;
import com.googlecode.clearnlp.util.UTInput;
import com.nicta.biomed.bnst13.SharedTaskHelper;
import com.nicta.biomed.bnst13.textprocess.GraphTransformer;

public class AnnotatedCPDoc extends AnnotatedDocImpl {
	/** class to handle a document annotated shared task annotations and parsed with 
	 * ClearParser */
	
	private static final Logger LOG = LoggerFactory.getLogger(AnnotatedCPDoc.class);
	String parseFile;
	private static JointReader depReader = new JointReader(0, 1, 2, 3, 4, 5, 6, 7, 8);
	protected String taskDataDir;
	private GraphTransformer graphTransformer = null;

	public AnnotatedCPDoc(String parseFile, String taskDataDir, boolean isTraining) throws IOException {
		this.parseFile = parseFile;
		String docId = SharedTaskHelper.docIdFromParsedFile(new File(parseFile).getName());
		setId(docId);
		this.taskDataDir = taskDataDir;
		this.isTraining = isTraining;
		LOG.debug("New annotated {} doc at {} with training dir {}", 
			isTraining ? "training": "test", this.parseFile, this.taskDataDir);
		init();
	}
	
	public void setGraphTransformer(GraphTransformer graphTransformer) {
		this.graphTransformer = graphTransformer;
	}
	
	public AnnotatedCPDoc(String parseFile, String taskDataDir) throws IOException {
		this(parseFile, taskDataDir, true);
	}

	protected String eventFile() {
		return SharedTaskHelper.eventFileForParsedFile(parseFile, taskDataDir);
	}

	protected String entityFile() {
		return SharedTaskHelper.entityFileForParsedFile(parseFile, taskDataDir);
	}
	
	public List<DEPTree> readParses() {
		List<DEPTree> results = new ArrayList<DEPTree>();
		depReader.open(UTInput.createBufferedFileReader(parseFile));
		DEPTree tree = null;
		while ((tree = depReader.next()) != null)
			results.add(tree);
		return results;
	}

	/* (non-Javadoc)
	 * @see com.nicta.biomed.bnst13.AnnotatedDocument#getAnnSentences()
	 */
	@Override
	public List<? extends AnnotatedSentence> getAnnSentences() {
		LOG.debug("Returning annotated sentences for {}", getId());
		List<AnnotatedSentence> annSents = new ArrayList<AnnotatedSentence>();
		for (AnnotatedClearparse annCp : getAnnotatedClearParses()) {
			AnnotatedSentence annSent = annCp.getAnnSentence();
			annSents.add(annSent);
		}
		return annSents;
	}
	
	public List<AnnotatedClearparse> getAnnotatedClearParses() {
		List<AnnotatedClearparse> annCps = new ArrayList<AnnotatedClearparse>();
		int sentId = 1;
		for (DEPTree tree :readParses()) {
			AnnotatedClearparse annCp = new AnnotatedClearparse(tree, termAnns, evtAnns, sentId++);
			if (graphTransformer != null)
				annCp.setTransformer(graphTransformer);
			annCps.add(annCp);
		}
		return annCps;
	}
		
}
