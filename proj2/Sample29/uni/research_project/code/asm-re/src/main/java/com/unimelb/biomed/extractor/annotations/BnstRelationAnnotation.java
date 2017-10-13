package com.unimelb.biomed.extractor.annotations;

import gov.nih.bnst.preprocessing.annotation.Relation;

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

public class BnstRelationAnnotation implements BnstAnnotation {
	private static final Logger LOG = LoggerFactory.getLogger(BnstEventAnnotation.class);

	private String id;
	private String relationType;
	private SortedMap<String, String> argsToIds = new TreeMap<String, String>();
	private Set<String> argIds = new HashSet<String>();

	public BnstRelationAnnotation(String line) {
		String[] id_argText = line.split("\t");
		id = id_argText[0];
		readArgs(id_argText[1]);
	}

	public BnstRelationAnnotation(String id, String relationType) {
		this.id = id;
		this.relationType = relationType;
	}

	private void readArgs(String argText) {
		String[] argComps = argText.split(" ");
        boolean isFirst = true;
        for (String comp : argComps) {
            //Use the first component as the type
            if (isFirst) {
                this.relationType = comp;
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
		builder.append(relationType);
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
		return relationType;
	}

    public void setRelationType(String type) {
        this.relationType = type;
    }

	public Relation asRelationInstance() {
		Relation rel = new Relation(id, relationType);
		for (Map.Entry<String, String> argEntry : argsToIds.entrySet()) {
			String argName = argEntry.getKey();
			String argId = argEntry.getValue();
			rel.addTheme(argId);
		}
		return rel;
	}

	public static List<BnstRelationAnnotation> readFile(String annsFile) throws IOException {
		List<BnstRelationAnnotation> anns =
            new ArrayList<BnstRelationAnnotation>();
		BufferedReader rdr = new BufferedReader(new InputStreamReader(
				new FileInputStream(annsFile)));
		try {
			String line;
			while ((line = rdr.readLine()) != null) {
				LOG.trace("Checking annotation line {}", line);
				if (line.startsWith("R"))
					anns.add(new BnstRelationAnnotation(line));
			}
		} finally {
			rdr.close();
		}
		LOG.debug("Read {} relation annotations from {}", anns.size(), annsFile);
		return anns;
	}
}
