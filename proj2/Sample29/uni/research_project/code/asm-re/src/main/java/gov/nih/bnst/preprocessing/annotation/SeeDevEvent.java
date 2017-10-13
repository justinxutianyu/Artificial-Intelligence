package gov.nih.bnst.preprocessing.annotation;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import edu.ucdenver.ccp.common.string.StringConstants;

public class SeeDevEvent {

	/** original event record in the ann file */
	private String eventRecord;

	/** eventID in the ann file that starts with capital letter R */
	private final String eventID;

	/** event category */
	private final String eventCategory;

	/** event themes */
	private List<String> eventThemes;

	/** sentenceID containing the event */
	private Integer eventSentenceID = null;

	/** sentence text containing the event */
	private String eventSentenceText = null;

	/**
	 * @param eventID
	 * @param eventCategory
	 * @param eventTrigger
	 * @param eventThemes
	 * @param eventCause
	 */
	public SeeDevEvent(
        String eventID,
        String eventCategory
    ) {
		super();
		this.eventID = eventID;
		this.eventCategory = eventCategory;
		this.eventThemes = new ArrayList<String>();
	}

	public void addTheme(String themeId) {
		this.eventThemes.add(themeId);
	}

	public void setSentenceID(Integer eventSentenceID) {
		this.eventSentenceID = eventSentenceID;
	}

	public Integer getSentenceID() {
		return eventSentenceID;
	}

	public void setSentenceText(String eventSentenceText) {
		this.eventSentenceText = eventSentenceText;
	}

	public String getSentenceText() {
		return eventSentenceText;
	}

	public String toANNString() {
		String annLine =
            eventID
            + StringConstants.TAB
            + eventCategory;
		if (eventThemes != null) {
			int index = 1;
			for (String theme : eventThemes) {
				String label = "Arg" + index;
				annLine += (" " + label + ":" + theme);
				index++;
			}
		}
		return annLine;
	}

	public String getSeeDevEventID(){
		return eventID;
	}

	public String getSeeDevEventCategory(){
		return eventCategory;
	}

	public List<String> getSeeDevEventThemes(){
		return eventThemes;
	}
}
