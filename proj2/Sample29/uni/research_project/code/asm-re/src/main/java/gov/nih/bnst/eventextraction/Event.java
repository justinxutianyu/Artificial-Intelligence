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

package gov.nih.bnst.eventextraction;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import gov.nih.bnst.patternlearning.EventRule;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

import edu.ucdenver.ccp.common.string.StringConstants;
import edu.uci.ics.jung.graph.DirectedGraph;

public class Event {

	/** eventID in the A2 file */
	private int eventID = -1;

	/** event category */
	private String eventCategory;

	/** event trigger */
	private Trigger eventTrigger;

	/** event themes, multiple for binding events */
	private Set<Vertex> eventThemes;

	/** event cause, optional */
	private Vertex eventCause = null;

	/** event node of the theme */
	private Vertex themeEvent = null;

	/** theme event category */
	private String themeEventCategory;

	/** event node of the cause */
	private Vertex causeEvent = null;

	/** cause event category */
	private String causeEventCategory;

	/** original sentence dependency graph */
	private DirectedGraph<Vertex, Edge> sentenceGraph;

	/** original event rule */
	private EventRule eventRule;

	/** associated event ids */
	Set<Integer> associatedEventIDs;

	/** status used when generating A2 */
	boolean status = false;

    public Event(EventRule eventRule) {
        this.eventRule = eventRule;
        associatedEventIDs = new HashSet<Integer>();
    }

    /**
     * use one event's information to update another event
     */
    public void update(Event event) {
        eventCategory = event.eventCategory;
        eventTrigger = event.eventTrigger;
        eventThemes = event.eventThemes;
        eventCause = event.eventCause;
        themeEvent = event.themeEvent;
        themeEventCategory = event.themeEventCategory;
        causeEvent = event.causeEvent;
        causeEventCategory = event.causeEventCategory;
        sentenceGraph = event.sentenceGraph;
    }

	public String toA2String() {
		String a2Line = eventID + StringConstants.TAB + eventCategory + StringConstants.COLON + eventTrigger;
		if (eventThemes != null) {
			for (Vertex theme : eventThemes) {
				a2Line += (" Theme:" + theme);
			}
		}
		if (eventCause != null) {
			a2Line += (" Cause:" + eventCause);
		}
		return a2Line;
	}

	/**
     * print raw event content
     * Example: Positive_regulation:(Induction-1/NN) Theme:(Negative_regulation:inhibits-2/VBZ)
     */
    @Override
	public String toString(){
    	StringBuilder sb = new StringBuilder();
    	sb.append(eventCategory);

        sb.append(":(");
        List<Vertex> sorted = new ArrayList<Vertex>(eventTrigger.getTriggerNodes());
		Collections.sort(sorted, new MyNewComparator());
		sb.append( join(sorted, " ") );
        sb.append(") ");

		if(!hasTheme() && hasCause()) {
			if(isCauseEvent()) {
				sb.append("Cause:(" + causeEventCategory + ":" + causeEvent + ") ");
			}
			else {
				sb.append("Cause:(" + eventCause + ") ");
			}
		}
		else if(hasTheme() && !hasCause()) {
			if(isThemeEvent()) {
				sb.append("Theme:(" + themeEventCategory + ":" + themeEvent + ") ");
			}
			else {
				List<Vertex> temp = new ArrayList<Vertex>(eventThemes);
				sb.append("Theme:(" + temp.get(0) + ") ");
				for(int i=1; i<temp.size(); i++) {
					sb.append("Theme" + (i+1) + ":(" + temp.get(i) + ") ");
				}
			}
		}
		else {
			if(isThemeEvent()) {
				sb.append("Theme:(" + themeEventCategory + ":" + themeEvent + ") ");
			}
			else {
				List<Vertex> temp = new ArrayList<Vertex>(eventThemes);
				sb.append("Theme:(" + temp.get(0) + ") ");
				for(int i=1; i<temp.size(); i++) {
					sb.append("Theme" + (i+1) + ":(" + temp.get(i) + ") ");
				}
			}
			if(hasCause()) {
				if(isCauseEvent()) {
					sb.append("Cause:(" + causeEventCategory + ":" + causeEvent + ") ");
				}
				else {
					sb.append("Cause:(" + eventCause + ") ");
				}
			}
		}
		return sb.toString();
    }

	public int getEventID(){
		return eventID;
	}

	public boolean getStatus() {
		return status;
	}

	public void setStatus(boolean status) {
		this.status = status;
	}

	public Set<Integer> getAssociatedEventIDs() {
		return associatedEventIDs;
	}

	public void setEventID(int eventID){
		this.eventID = eventID;
	}

	public String getEventCategory(){
		return eventCategory;
	}

	public Set<Vertex> getEventThemes() {
		return eventThemes;
	}

	public void setEventThemes(Set<Vertex> eventThemes) {
		this.eventThemes = eventThemes;
	}

	public void setEventCause(Vertex eventCause) {
		this.eventCause = eventCause;
	}

	public Vertex getEventCause() {
		return eventCause;
	}

	public void setEventTrigger(Trigger eventTrigger) {
		this.eventTrigger = eventTrigger;
	}

	public void setEventCategory(String eventCategory){
		this.eventCategory = eventCategory;
	}

	 /**
     * check isThemeEvent
     */
    public boolean isThemeEvent() {
    	return this.themeEvent != null;
    }

    public Vertex getThemeEvent() {
    	return themeEvent;
    }

    public void setThemeEvent(Vertex themeEvent) {
    	this.themeEvent = themeEvent;
    }

    public String getThemeEventCategory() {
    	return themeEventCategory;
    }

    public void setThemeEventCategory(String themeEventCategory) {
        this.themeEventCategory = themeEventCategory;
    }

    /**
     * check isCauseEvent
     */
    public boolean isCauseEvent() {
    	return this.causeEvent != null;
    }

    public Vertex getCauseEvent() {
    	return causeEvent;
    }

    public void setCauseEvent(Vertex causeEvent) {
    	this.causeEvent = causeEvent;
    }

    public String getCauseEventCategory() {
    	return causeEventCategory;
    }

    public void setCauseEventCategory(String causeEventCategory) {
        this.causeEventCategory = causeEventCategory;
    }

    /**
     * check if the event has a theme
     */
    public boolean hasTheme() {
    	return eventThemes != null;
    }

    public boolean hasCause() {
		return this.eventCause != null;
	}

    public void setSentenceGraph(DirectedGraph<Vertex, Edge> sentenceGraph) {
    	this.sentenceGraph = sentenceGraph;
    }

    public DirectedGraph<Vertex, Edge> getSentenceGraph() {
    	return sentenceGraph;
    }

    public Trigger getEventTrigger() {
    	return eventTrigger;
    }

    public EventRule getOriginalEventRule() {
    	return eventRule;
    }

    public void setOriginalEventRule(EventRule eventRule) {
    	this.eventRule = eventRule;
    }

    public static final String join(List<Vertex> c, String delimiter) {
		if (c.isEmpty()) {
			return "";
		}
		StringBuffer buffer = new StringBuffer(c.get(0).toString());
		for(int i=1; i<c.size(); i++) {
			buffer.append(delimiter).append(c.get(i).toString());
		}
		return buffer.toString();
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((eventCategory == null) ? 0 : eventCategory.hashCode());
		result = prime * result
				+ ((eventCause == null) ? 0 : eventCause.hashCode());
		result = prime * result
				+ ((eventThemes == null) ? 0 : eventThemes.hashCode());
		result = prime * result
				+ ((eventTrigger == null) ? 0 : eventTrigger.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Event other = (Event) obj;
		if (eventCategory == null) {
			if (other.eventCategory != null)
				return false;
		} else if (!eventCategory.equals(other.eventCategory))
			return false;
		if (eventCause == null) {
			if (other.eventCause != null)
				return false;
		} else if (!eventCause.equals(other.eventCause))
			return false;
		if (eventThemes == null) {
			if (other.eventThemes != null)
				return false;
		} else if (!eventThemes.equals(other.eventThemes))
			return false;
		if (eventTrigger == null) {
			if (other.eventTrigger != null)
				return false;
		} else if (!eventTrigger.equals(other.eventTrigger))
			return false;
		return true;
	}
}
