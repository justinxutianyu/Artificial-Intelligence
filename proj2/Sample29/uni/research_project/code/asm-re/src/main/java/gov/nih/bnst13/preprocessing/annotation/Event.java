/*
 Copyright (c) 2012, Regents of the University of Colorado
 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, 
 are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this 
    list of conditions and the following disclaimer.

 * Redistributions in binary form must reproduce the above copyright notice, 
    this list of conditions and the following disclaimer in the documentation 
    and/or other materials provided with the distribution.

 * Neither the name of the University of Colorado nor the names of its 
    contributors may be used to endorse or promote products derived from this 
    software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
 DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
 ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

package gov.nih.bnst13.preprocessing.annotation;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import edu.ucdenver.ccp.common.string.StringConstants;

public class Event {

	/** original event record in the A2 file */
	private String eventRecord;

	/** eventID in the A2 file that starts with capital letter E */
	private final String eventID;

	/** event category */
	private final String eventCategory;

	/** event trigger */
	private final String eventTrigger;

	/** event themes, multiple for binding events */
	private List<String> eventThemes;

	/** event cause, optional */
	private String eventCause = null;

	/** sentenceID containing the event */
	private Integer eventSentenceID = null;
	
	/** sentence text containing the event */
	private String eventSentenceText = null;
	
	/**
	 * Constructor to directly use record line to initialize the class fields
	 * 
	 * @param record
	 */
	public Event(String record) {
		Pattern pattern = Pattern.compile("^(E\\d+)\\t(\\w+):(\\w+)\\s(Theme(\\d)?:.+)$");
		Matcher m = pattern.matcher(record);
		if (!m.find())
			throw new RuntimeException("The event record: " + record + " is not valid. Please check.");
		eventRecord = record;
		eventID = m.group(1);
		eventCategory = m.group(2);
		eventTrigger = m.group(3);
		eventThemes = new ArrayList<String>();
		String leftover = m.group(4);
		String[] arguments = leftover.split("\\s+");
		if (eventCategory.equals("Positive_regulation") ||
		 eventCategory.equals("Regulation") ||
				eventCategory.equals("Negative_regulation")) {
			for (String argument : arguments) {
				Matcher p = Pattern.compile("^Theme:(\\w+)$").matcher(argument);
				if (p.find()) {
					eventThemes.add(p.group(1));
					continue;
				}
				p = Pattern.compile("^Cause:(\\w+)$").matcher(argument);
				if (p.find()) {
					eventCause = p.group(1);
				}
			}
		} else {
			for (String argument : arguments) {
				Matcher p = Pattern.compile("^Theme\\d?:(\\w+)$").matcher(argument);
				if (p.find()) {
					eventThemes.add(p.group(1));
				}
			}
		}
	}

	/**
	 * @param eventID
	 * @param eventCategory
	 * @param eventTrigger
	 * @param eventThemes
	 * @param eventCause
	 */
	public Event(String eventID, String eventCategory, String eventTrigger) {
		super();
		this.eventID = eventID;
		this.eventCategory = eventCategory;
		this.eventTrigger = eventTrigger;
		this.eventThemes = new ArrayList<String>();
	}

	public void addTheme(String themeId) {
		this.eventThemes.add(themeId);
	}

	public void setCause(String causeId) {
		this.eventCause = causeId;
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

	public boolean hasCause() {
		return this.eventCause != null;
	}

	public String toA2String() {
		String a2Line = eventID + StringConstants.TAB + eventCategory + StringConstants.COLON + eventTrigger;
		if (eventThemes != null) {
			int index = 1;
			for (String theme : eventThemes) {
				String label = "Theme" + (index > 1 ? index : "");
				a2Line += (" " + label + ":" + theme);
				index++;
			}
		}
		if (eventCause != null) {
			a2Line += (" Cause:" + eventCause);
		}
		return a2Line;
	}
	
	public String getEventID(){
		return eventID;
	}
	
	public String getEventCategory(){
		return eventCategory;
	}
	
	public String getEventCause(){
		return eventCause;
	}
	
	public String getEventTrigger(){
		return eventTrigger;
	}

	public List<String> getEventThemes(){
		return eventThemes;
	}
}
