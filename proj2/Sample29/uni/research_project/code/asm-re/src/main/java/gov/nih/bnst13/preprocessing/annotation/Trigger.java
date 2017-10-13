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

import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


import edu.ucdenver.ccp.common.string.StringConstants;
import gov.nih.bnst13.preprocessing.dp.Vertex;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * class that generates a trigger object
 */
public class Trigger {

	private static final Logger LOG  = LoggerFactory.getLogger(Trigger.class);

	/** original trigger record in the A2 file */
	private final String triggerRecord;

	/** triggerID in the A2 file that starts with capital letter T */
	private final String triggerID;

	/** trigger category */
	private final String triggerCategory;

	/** specific trigger name */
	private final String triggerName;

	/** the start index of the trigger */
	private final int startIndex;

	/**
	 * according to the definition in BioNLP09, the endIndex is the startIndex +
	 * length(triggerName), and corresponds to the index of the next byte
	 */
	private final int endIndex;
	
	/** corresponding dependency graph nodes of the trigger */
	private Set<Vertex> triggerNodes;
	
	/** centerNode of the trigger nodes */
	private Vertex centerNode;

	/**
	 * Constructor to directly use record line to initialize the class fields
	 * 
	 * @param record
	 */
	public Trigger(String record) {
		Pattern pattern = Pattern.compile("^(T\\d+)\\t(\\w+)\\s(\\d+)\\s(\\d+)(?:\\t(.+))?$");
		Matcher m = pattern.matcher(record);
		if (!m.find())
			throw new RuntimeException("The trigger record: " + record + " is not valid. Please check.");
		triggerRecord = record;
		triggerID = m.group(1);
		triggerCategory = m.group(2);
		startIndex = Integer.parseInt(m.group(3));
		endIndex = Integer.parseInt(m.group(4));
		if (m.group(5) == null) {
			LOG.error("Invalid trigger pattern '{}'; the trigger name is missing", m.group(5));
			triggerName = "";
		} else {
			triggerName = m.group(5);
		}

	}

	/**
	 * @param triggerID
	 * @param triggerCategory
	 * @param triggerName
	 * @param startIndex
	 * @param endIndex
	 */
	public Trigger(String triggerID, String triggerCategory, String triggerName, int startIndex, int endIndex) {
		super();
		this.triggerID = triggerID;
		this.triggerCategory = triggerCategory;
		this.triggerName = triggerName;
		this.startIndex = startIndex;
		this.endIndex = endIndex;
		this.triggerRecord = triggerID + StringConstants.TAB + triggerCategory + StringConstants.SPACE + startIndex
				+ StringConstants.SPACE + endIndex + StringConstants.TAB + triggerName;
	}

	public String toA2String() {
		return triggerRecord;
	}
	
	public String getTriggerID(){
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
	
	public void setTriggerCenterNode(Vertex centerNode) {
		this.centerNode = centerNode;
	}
	public Vertex getTriggerCenterNode() {
		return centerNode;
	}
}
