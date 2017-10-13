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
 * class definition for coreference annotation
 * @author liuh11
 *
 */
public class Coreference {

	/** original coreference record in the A2 file */
	private String coreferenceRecord;

	/** coreferenceID in the A2 file that starts with capital letter R */
	private final String coreferenceID;

	/** coreference subject: anaphora */
	private String coreferenceSubject;

	/** coreference object: protein */
	private String coreferenceObject;

	/** sentenceID containing the coreference */
	private Integer coreferenceSentenceID = null;
	
	/** sentence text containing the coreference */
	private String coreferenceSentenceText = null;
	
	/**
	 * Constructor to directly use record line to initialize the class fields
	 * 
	 * @param record
	 */
	public Coreference(String record) {
		Pattern pattern = Pattern.compile("^(R\\d+)\\tCoreference\\s(Subject):(\\w+)\\s(Object):(\\w+)$");
		Matcher m = pattern.matcher(record);
		if (!m.find())
			throw new RuntimeException("The coreference record: " + record + " is not valid. Please check.");
		coreferenceRecord = record;
		coreferenceID = m.group(1);
		coreferenceSubject = m.group(3);
		coreferenceObject = m.group(5);
	}

	/**
	 * @param coreferenceID
	 * @param coreferenceSubject
	 * @param coreferenceObject
	 */
	public Coreference(String coreferenceID, String coreferenceSubject, String coreferenceObject) {
		super();
		this.coreferenceID = coreferenceID;
		this.coreferenceSubject = coreferenceSubject;
		this.coreferenceObject = coreferenceObject;
	}

	public void setSentenceID(Integer coreferenceSentenceID) {
		this.coreferenceSentenceID = coreferenceSentenceID;
	}
	
	public Integer getSentenceID() {
		return coreferenceSentenceID;
	}
	
	public void setSentenceText(String coreferenceSentenceText) {
		this.coreferenceSentenceText = coreferenceSentenceText;
	}
	
	public String getSentenceText() {
		return coreferenceSentenceText;
	}

	public String toA2String() { 
		String a2Line = coreferenceID + StringConstants.TAB + "Copreference Subject" + StringConstants.COLON + 
		                                 coreferenceSubject + " Object" + StringConstants.COLON + coreferenceObject;
		return a2Line;
	}
	
	public String getCoreferenceID(){
		return coreferenceID;
	}
	
	
	public String getCoreferenceSubject(){
		return coreferenceSubject;
	}

	public String getCoreferenceObject(){
		return coreferenceObject;
	}

}
