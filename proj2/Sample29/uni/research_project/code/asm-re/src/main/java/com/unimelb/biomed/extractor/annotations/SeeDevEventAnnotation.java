package com.unimelb.biomed.extractor.annotations;

import gov.nih.bnst.preprocessing.annotation.SeeDevEvent;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.SortedMap;
import java.util.TreeMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SeeDevEventAnnotation implements BnstAnnotation {
	private static final Logger LOG = LoggerFactory.getLogger(BnstEventAnnotation.class);

	private String id;
	private String eventType;
	private SortedMap<String, String> argsToIds = new TreeMap<String, String>();
	private Set<String> argIds = new HashSet<String>();

	public SeeDevEventAnnotation(String line) {
		String[] id_argText = line.split("\t");
		id = id_argText[0];
		readArgs(id_argText[1]);
	}

	public SeeDevEventAnnotation(String id, String eventType) {
		this.id = id;
		this.eventType = eventType;
	}

	private void readArgs(String argText) {
		String[] argComps = argText.split(" ");
        boolean isFirst = true;
        for (String comp : argComps) {
            //Use the first component as the type
            if (isFirst) {
                this.eventType = comp;
                isFirst = false;
                continue;
            }
            String[] type_termId = comp.split(":");
            String type = type_termId[0];
            String termId = type_termId[1];
            this.argIds.add(termId);
			this.argsToIds.put(type, termId);
		}
	}

	public void addArg(String type, String termId) {
		argsToIds.put(type, termId);
	}

	public String getId() {
		return id;
	}

	public String getArgText() {
		StringBuilder builder = new StringBuilder();
		builder.append(eventType);
		for (Map.Entry<String, String> argEntry : argsToIds.entrySet()) {
			builder.append(" ");
			builder.append(argEntry.getKey());
			builder.append(":");
			builder.append(argEntry.getValue());
		}
		return builder.toString();
	}

	public Set<String> getArgIds() {
		return argIds;
	}

	public SortedMap<String, String> getArgsToIds() {
		return argsToIds;
	}

	public String toString() {
		return id + "\t" + getArgText();
	}

	public String getRelationType() {
		return eventType;
	}

    public void setRelationType(String type) {
        this.eventType = type;
    }

	public SeeDevEvent asSeeDevEventInstance() {
		SeeDevEvent rel = new SeeDevEvent(id, eventType);
		for (Map.Entry<String, String> argEntry : argsToIds.entrySet()) {
			String argName = argEntry.getKey();
			String argId = argEntry.getValue();
			rel.addTheme(argId);
		}
		return rel;
	}

	public static List<SeeDevEventAnnotation> readFile(String annsFile) throws IOException {
		List<SeeDevEventAnnotation> anns =
            new ArrayList<SeeDevEventAnnotation>();
		BufferedReader rdr = new BufferedReader(new InputStreamReader(
				new FileInputStream(annsFile)));
		try {
			String line;
			while ((line = rdr.readLine()) != null) {
				LOG.trace("Checking annotation line {}", line);
				if (line.startsWith("E"))
					anns.add(new SeeDevEventAnnotation(line));
			}
		} finally {
			rdr.close();
		}
		LOG.debug("Read {} event annotations from {}", anns.size(), annsFile);
		return anns;
	}
}
