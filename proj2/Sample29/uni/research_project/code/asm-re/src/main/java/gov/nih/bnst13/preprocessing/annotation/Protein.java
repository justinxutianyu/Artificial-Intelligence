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

/**
 * class that generates a protein object
 */
public class Protein {

	/** original protein record in the A1 file */
	private final String proteinRecord;

	/** proteinID in the A1 file that starts with capital letter T */
	private final String proteinID;

	/** specific protein name */
	private String proteinName;

	/** the start index of the protein name */
	private int startIndex;

	/**
	 * according to the definition in BioNLP09, the endIndex is the startIndex +
	 * length(proteinName), and corresponds to the index of the next byte
	 */
	private int endIndex;
	
	/** corresponding dependency graph node of the protein */
	private Vertex graphNode;

	/**
	 * Constructor to directly use record line to initialize the class fields
	 * 
	 * @param record
	 */
	public Protein(String record) {
		Pattern pattern = Pattern.compile("^(T\\d+)\\tProtein\\s(\\d+)\\s(\\d+)\\t(.+)$");
		Matcher m = pattern.matcher(record);
		if (!m.find())
			throw new RuntimeException("The protein record: " + record + " is not valid. Please check.");
		proteinRecord = record;
		proteinID = m.group(1);
		startIndex = Integer.parseInt(m.group(2));
		endIndex = Integer.parseInt(m.group(3));
		proteinName = m.group(4);
		// System.out.println(proteinID + " "+proteinName+" "+startIndex+ " "+endIndex);
	}

	/**
	 * @param proteinID
	 * @param proteinName
	 * @param startIndex
	 * @param endIndex
	 */
	public Protein(String proteinID, String proteinName, int startIndex, int endIndex) {
		super();
		this.proteinID = proteinID;
		this.proteinName = proteinName;
		this.startIndex = startIndex;
		this.endIndex = endIndex;
		this.proteinRecord = proteinID + StringConstants.TAB + "Protein " + startIndex + " " + endIndex
				+ StringConstants.TAB + proteinName;
	}

	public String toA1String() {
		return proteinRecord;
	}
	
	public String getProteinID(){
		return proteinID;
	}
	
	public String getProteinName(){
		return proteinName;
	}
    
	public void setProteinName(String proteinName){
		this.proteinName = proteinName;
	}
	
	public void setStartIndex(int startIndex) {
		this.startIndex = startIndex;
	}
	
	public void setEndIndex(int endIndex) {
		this.endIndex = endIndex;
	}
	
	public int getStartIndex() {
		return startIndex;
	}
	
	public int getEndIndex() {
		return endIndex;
	}
	
	public void setGraphNode(Vertex graphNode) {
		this.graphNode = graphNode;
	}
	
	public Vertex getGraphNode() {
		return graphNode;
	}
}
