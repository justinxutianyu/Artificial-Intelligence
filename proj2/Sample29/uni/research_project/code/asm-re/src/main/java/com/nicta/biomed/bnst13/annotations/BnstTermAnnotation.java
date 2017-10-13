package com.nicta.biomed.bnst13.annotations;

import gov.nih.bnst13.preprocessing.annotation.Protein;
import gov.nih.bnst13.preprocessing.annotation.Trigger;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.util.Span;

public class BnstTermAnnotation implements BnstAnnotation {
	private static final Logger LOG = LoggerFactory.getLogger(BnstTermAnnotation.class);

	public static final String TERM_PREFIX = "T";

	private String id;
	private String name;
	private Span span;
	private String origText;
	private boolean isTrigger = false;
	
	public boolean isTrigger() {
		return isTrigger;
	}

	public void setTrigger(boolean isTrigger) {
		this.isTrigger = isTrigger;
	}

	public String getId() {
		return id;
	}
	
	/** returns the ID as an integer (after stripping off the leading 'T' */
	public int getIntegerId() {
		return Integer.parseInt(id.substring(TERM_PREFIX.length()));
	}

	public void setId(String id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Span getSpan() {
		return span;
	}

	public void setSpan(Span span) {
		this.span = span;
	}

	public String getOrigText() {
		return origText;
	}

	public void setOrigText(String origText) {
		this.origText = origText;
	}

	public BnstTermAnnotation(String sourceLine, boolean isTrigger) {
		String[] info = sourceLine.split("\t");
		id = info[0];
		String[] neInfo = info[1].split(" ");
		name = neInfo[0];
		int begin = Integer.parseInt(neInfo[1]);
		int end = Integer.parseInt(neInfo[2]);
		span = new Span(begin, end);
		origText = info[2];
		this.isTrigger = isTrigger;
	}

	public BnstTermAnnotation(String id, String name, Span span, String origText) {
		this(id, name, span, origText, false);
	}

	public BnstTermAnnotation(String id, String name, Span span, String origText, boolean isTrigger) {
		this.id = id;
		this.name = name;
		this.span = span;
		this.origText = origText;
	}

	public String toString() {
		return id + "\t" + name + " " + span.begin + " " + span.end + "\t" + origText;
	}

	public static List<BnstTermAnnotation> readFile(String annsFile) throws IOException {
		return readFile(annsFile, false);
	}

	public static List<BnstTermAnnotation> readFile(String annsFile, boolean areTriggers)
			throws IOException {
		List<BnstTermAnnotation> anns = new ArrayList<BnstTermAnnotation>();
		BufferedReader rdr = new BufferedReader(
				new InputStreamReader(new FileInputStream(annsFile)));
		try {
			String line;
			while ((line = rdr.readLine()) != null) {
				LOG.trace("Checking annotation line {}", line);
				if (line.startsWith(TERM_PREFIX))
					anns.add(new BnstTermAnnotation(line, areTriggers));
			}
		} finally {
			rdr.close();
		}
		LOG.debug("Read {} term annotations from {}", anns.size(), annsFile);
		return anns;
	}

	public Protein asProteinInstance() {
		LOG.trace("Creating new protein annotatation: {}, {}, {}", id, name, span);
		return new Protein(id, name, span.begin, span.end);
	}

	public Trigger asTriggerInstance() {
		return new Trigger(id, name, origText, span.begin, span.end);
	}
}
