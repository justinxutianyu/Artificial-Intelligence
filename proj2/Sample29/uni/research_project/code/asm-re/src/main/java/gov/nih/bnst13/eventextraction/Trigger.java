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
package gov.nih.bnst13.eventextraction;

import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import gov.nih.bnst13.preprocessing.dp.Vertex;

import edu.ucdenver.ccp.common.string.StringConstants;

/**
 * class that generates a trigger object
 */
public class Trigger {

	/** original trigger record in the A2 file */
	private String triggerRecord;

	/** triggerID in the A2 file that starts with capital letter T */
	private int triggerID = -1;

	/** trigger category */
	private String triggerCategory;

	/** specific trigger name */
	private String triggerName;

	/** the start index of the trigger */
	private int startIndex;

	/**
	 * according to the definition in BioNLP09, the endIndex is the startIndex +
	 * length(triggerName), and corresponds to the index of the next byte
	 */
	private int endIndex;
	
	/** corresponding dependency graph nodes of the trigger */
	private Set<Vertex> triggerNodes;
	
	/** centerNode of the trigger nodes */
	private Vertex centerNode = null;

	/**
	 * constructor for testing data
	 */
	public Trigger(Set<Vertex> triggerNodes) {
		this.triggerNodes = triggerNodes;
	}

	public String toA2String() {
		return triggerRecord;
	}
	
	public void setTriggerRecord(String triggerRecord) {
		this.triggerRecord = triggerRecord;
	}
	
	public int getTriggerID(){
		return triggerID;
	}
	
	public String getTriggerName(){
		return triggerName;
	}
	
	public String getTriggerCategory(){
		return triggerCategory;
	}
	
	public String getTriggerSpan(){
		return Integer.toString(startIndex) + "-" + Integer.toString(endIndex-1);
	}
	
	public int getStartIndex() {
		return startIndex;
	}
	
	public int getEndIndex() {
		return endIndex;
	}
	
	public void setTriggerNodes(Set<Vertex> triggerNodes) {
		this.triggerNodes = triggerNodes;
	}
	
	public Set<Vertex> getTriggerNodes() {
		return triggerNodes;
	}
	
	public void setCenterNodes(Vertex centerNode) {
		this.centerNode = centerNode;
	}
	
	public Vertex getCenterNode() {
		return centerNode;
	}
	
	public void setTriggerCenterNode(Vertex centerNode) {
		this.centerNode = centerNode;
	}
	
	public Vertex getTriggerCenterNode() {
		return centerNode;
	}
	
	public void setTriggerID(int triggerID) {
		this.triggerID= triggerID;
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((triggerNodes == null) ? 0 : triggerNodes.hashCode());
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
		Trigger other = (Trigger) obj;
		if (triggerNodes == null) {
			if (other.triggerNodes != null)
				return false;
		} else if (!triggerNodes.equals(other.triggerNodes))
			return false;
		return true;
	}
	
}
