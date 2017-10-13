package com.unimelb.biomed.extractor.annotations;

import gov.nih.bnst.preprocessing.annotation.Event;

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

public class BnstEventAnnotation implements BnstAnnotation {
	private static final Logger LOG = LoggerFactory.getLogger(BnstEventAnnotation.class);

	private String id;
	private String eventType;
	private String triggerId;
	private SortedMap<String, String> argsToIds = new TreeMap<String, String>();
	private Set<String> triggerAndArgIds = new HashSet<String>();

	public BnstEventAnnotation(String line) {
		String[] id_argText = line.split("\t");
		id = id_argText[0];
		readTriggersAndArgs(id_argText[1]);
	}

    public BnstEventAnnotation(String line, String corpus) {
		String[] id_argText = line.split("\t");
		id = id_argText[0];
		readTriggersAndArgs(id_argText[1], corpus);
	}

	public BnstEventAnnotation(String id, String eventType, String triggerId) {
		this.id = id;
		this.eventType = eventType;
		this.triggerId = triggerId;
	}


	private void readTriggersAndArgs(String argText) {
		String[] argComps = argText.split(" ");
		boolean isFirst = true;
		for (String comp : argComps) {
			String[] type_termId = comp.split(":");
			String type = type_termId[0];
			String termId = type_termId[1];
			triggerAndArgIds.add(termId);
			if (isFirst) {
				eventType = type;
				triggerId = termId;
				isFirst = false;
				continue;
			}
			argsToIds.put(type, termId);
		}
	}

    /**
    Read arguments/themes from an event/relation annotation.
    <p>
    Arguments or themes are specified by the string following the ID
    of the annotation, which is typically separated from the ID using
    a tab character. For example: E1\t<argText>.
    <p>
    The format of the argText string differs according to the corpus
    the annotation has been drawn from. The corpus parameter is used
    to specify which corpus we are parsing.

    @param argText
    The String describing the themes/arguments.

    @param corpus
    The corpus the annotation has been drawn from.

    @return
    void
    */
    private void readTriggersAndArgs(String argText, String corpus) {
		String[] argComps = argText.split(" ");
		boolean isFirst = true;
		for (String comp : argComps) {
            //In the Variome and SeeDev corpora, the event type is
            //specified as single word following the event ID.
            if ((corpus.equals("seedev") || corpus.equals("variome")) && isFirst) {
                eventType = comp;
                triggerId = null;
                isFirst = false;
                continue;
            }
            String[] type_termId = comp.split(":");
			String type = type_termId[0];
			String termId = type_termId[1];
			triggerAndArgIds.add(termId);
			if (isFirst) {
				eventType = type;
				triggerId = termId;
				isFirst = false;
				continue;
			}
			argsToIds.put(type, termId);
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
		builder.append(":");
		builder.append(triggerId);
		for (Map.Entry<String, String> argEntry : argsToIds.entrySet()) {
			builder.append(" ");
			builder.append(argEntry.getKey());
			builder.append(":");
			builder.append(argEntry.getValue());
		}
		return builder.toString();
	}

	public Set<String> getTriggerAndArgIds() {
		return triggerAndArgIds;
	}

	public SortedMap<String, String> getArgsToIds() {
		return argsToIds;
	}


	public String toString() {
		return id + "\t" + getArgText();
	}

	public String getEventType() {
		return eventType;
	}

	public String getTriggerId() {
		return triggerId;
	}

	public Event asEventInstance() {
		Event evt = new Event(id, eventType, triggerId);
		for (Map.Entry<String, String> argEntry : argsToIds.entrySet()) {
			String argName = argEntry.getKey();
			String argId = argEntry.getValue();
			if (argName.startsWith("Theme"))
				evt.addTheme(argId);
			else if (argName.startsWith("Cause"))
				evt.setCause(argId);
		}
		return evt;
	}

    public Event asThemeEventInstance() {
		Event evt = new Event(id, eventType, triggerId);
		for (Map.Entry<String, String> argEntry : argsToIds.entrySet()) {
			String argName = argEntry.getKey();
			String argId = argEntry.getValue();
			evt.addTheme(argId);
            evt.addThemeToTypeMapping(argId, argName);
		}
		return evt;
	}

	public static List<BnstEventAnnotation> readFile(String annsFile, String corpus) throws IOException {
		List<BnstEventAnnotation> anns = new ArrayList<BnstEventAnnotation>();
		BufferedReader rdr = new BufferedReader(new InputStreamReader(
				new FileInputStream(annsFile)));
		try {
			String line;
			while ((line = rdr.readLine()) != null) {
				LOG.trace("Checking annotation line {}", line);
				if (line.startsWith("E") || line.startsWith("R"))
					anns.add(new BnstEventAnnotation(line, corpus));
			}
		} finally {
			rdr.close();
		}
		LOG.debug("Read {} event annotations from {}", anns.size(), annsFile);
		return anns;
	}
}
