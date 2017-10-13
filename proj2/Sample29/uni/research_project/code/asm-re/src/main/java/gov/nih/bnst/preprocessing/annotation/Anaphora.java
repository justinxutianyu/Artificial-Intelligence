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
package gov.nih.bnst.preprocessing.annotation;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import edu.ucdenver.ccp.common.string.StringConstants;

/**
 * class that generates a anaphora object
 */
public class Anaphora {

	/** original anaphora record in the A2 file */
	private final String anaphoraRecord;

	/** anaphoraID in the A2 file that starts with capital letter T */
	private final String anaphoraID;

	/** specific anaphora name */
	private final String anaphoraName;

	/** the start index of the anaphora */
	private final int startIndex;

	/**
	 * according to the definition in BioNLP09, the endIndex is the startIndex +
	 * length(anaphoraName), and corresponds to the index of the next byte
	 */
	private final int endIndex;

	/**
	 * Constructor to directly use record line to initialize the class fields
	 * 
	 * @param record
	 */
	public Anaphora(String record) {
		Pattern pattern = Pattern.compile("^(T\\d+)\\t(\\w+)\\s(\\d+)\\s(\\d+)\\t(.+)$");
		Matcher m = pattern.matcher(record);
		if (!m.find())
			throw new RuntimeException("The anaphora record: " + record + " is not valid. Please check.");
		anaphoraRecord = record;
		anaphoraID = m.group(1);
		startIndex = Integer.parseInt(m.group(3));
		endIndex = Integer.parseInt(m.group(4));
		anaphoraName = m.group(5);
	}

	/**
	 * @param anaphoraID
	 * @param anaphoraCategory
	 * @param anaphoraName
	 * @param startIndex
	 * @param endIndex
	 */
	public Anaphora(String anaphoraID, String anaphoraName, int startIndex, int endIndex) {
		super();
		this.anaphoraID = anaphoraID;
		this.anaphoraName = anaphoraName;
		this.startIndex = startIndex;
		this.endIndex = endIndex;
		this.anaphoraRecord = anaphoraID + StringConstants.TAB + "Anaphora" + StringConstants.SPACE + startIndex
				+ StringConstants.SPACE + endIndex + StringConstants.TAB + anaphoraName;
	}

	public String toA2String() {
		return anaphoraRecord;
	}
	
	public String getAnaphoraID(){
		return anaphoraID;
	}
	
	public String getAnaphoraName(){
		return anaphoraName;
	}
	
	public String getAnaphoraSpan(){
		return Integer.toString(startIndex) + "-" + Integer.toString(endIndex-1);
	}
    
	public int getStartIndex() {
		return startIndex;
	}
	
	public int getEndIndex() {
		return endIndex;
	}
}
