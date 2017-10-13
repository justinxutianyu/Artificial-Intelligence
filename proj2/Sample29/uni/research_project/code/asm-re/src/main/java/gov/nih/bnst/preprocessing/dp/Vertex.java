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

package gov.nih.bnst.preprocessing.dp;

import gov.nih.bnst.preprocessing.pt.Token;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


/**
 * <p>Definition of DepNodeVertex for dependency graphs</p>
 *
 * <p>DepNodeVertex is then fed into graphs of the JUNG library</p>
 *
 * <p>The DepNodeVertex definition can be modified based on one's own needs</p>
 *
 * @author Implemented by Haibin Liu and Tested by Philippe Thomas
 *
 */
public class Vertex implements edu.ucdenver.ccp.esm.Vertex {
	private static final Logger LOG = LoggerFactory.getLogger(Vertex.class);

	public static final String BIO_ENTITY = "BIO_Entity";
    public static final String ARG_PREFIX = "ARG_";

	/** original entire token including position number */
    private String token;

    /** sentence token only */
    private String word;

    /** lemma of word */
    private String lemma;

    /** POS tag */
    private String tag;

    /** token position */
    private int pos;

    /** offset position relative to the entire document */
    private int offset;

    /** corresponding PTB tree token of the node */
    private Token treeToken;

    /** for quick POS comparison */
    private String generalizedPOS;

    /** for quick node comparison */
    private String compareForm;

    /** check if it's a protein node, defaulted to be false */
    private boolean isProtein;

    /** protein ID associated with the node */
    private String proteinID;

    /** check if it's an argument node, default to false */
    private boolean isArgument;

    /** argument ID associated with the node */
    private String argumentID;

    /** check if it's a trigger node, defaulted to be false */
    private boolean isTrigger;

    /** trigger ID associated with the node */
    private String triggerID;

    /**
	 * Construtor to initialize the class field
	 */
    public Vertex (String token) {
        this.token = token;
        Matcher m = Pattern.compile("^(.+)-(\\d+)\\x27*$").matcher(token);
        //Matcher m = Pattern.compile("^(.+)-(\\d+)\\x27*\\/(.+)$").matcher(token);
        if(!m.find())
        	throw new RuntimeException("The node: "
					+ token + " is not valid. Please check.");
        word = m.group(1);
	    pos = Integer.parseInt( m.group(2) );
	    tag = "";
	    isProtein = false;
	    proteinID = "";
	    isTrigger = false;
	    triggerID = "";
    }

    /**
	 * Construtor to initialize the class field
	 */
    public Vertex (String token, String mode) {
    	if(mode.equals("test") || mode.equals("withpos")) {
    		this.token = token;
            //Matcher m = Pattern.compile("^(.+)-(\\d+)\\x27*$").matcher(token);
            Matcher m = Pattern.compile("^(.+)-(\\d+)\\x27*\\/(.*)$").matcher(token);
            if(!m.find())
            	throw new RuntimeException("The node: "
    					+ token + " is not valid. Please check.");
            word = m.group(1);
    	    pos = Integer.parseInt( m.group(2) );
    	    tag = m.group(3);
    	    if(word.startsWith(BIO_ENTITY)) {
    	    	isProtein = true;
    	    	proteinID = "T" + word.substring(BIO_ENTITY.length());
            } else if (word.startsWith(ARG_PREFIX)) {
                Matcher vm = Pattern.compile("^ARG_([a-z]+)(.+)$").matcher(word);
                vm.find();
                this.word = vm.group(1);
                this.isArgument = true;
                this.argumentID = "T" + vm.group(2);
            } else {
    	    	isProtein = false;
        	    proteinID = "";
    	    }
    	    isTrigger = false;
    	    triggerID = "";
    		LOG.info("Constructing new Vertex from: '{}', with word '{}', location {}, tag '{}', argumentID {}, proteinID '{}': '{}'",
    				token, word, pos, tag, argumentID, proteinID, this);
    	}
    	else throw new RuntimeException("Wrong constructor mode " + mode);
    }

    /**
	 * default Construtor to initialize the class fields to empty
	 */
    public Vertex () {
	    compareForm = "";
	    generalizedPOS =   "";
	    lemma = "";
	    pos = -1;
	    offset = -1;
	    tag = "";
	    token = "";
	    word = "";
	    isProtein = false;
	    proteinID = "";
	    isTrigger = false;
	    triggerID = "";
    }

    /**
     * use one node's information to update another node
     */
    protected void update (Vertex target) {
	    compareForm = target.compareForm;
	    generalizedPOS = target.generalizedPOS;
	    lemma = target.lemma;
	    pos = target.pos;
	    offset = target.offset;
	    tag = target.tag;
	    token = target.token;
	    word = target.word;
	    treeToken = target.treeToken;
	    isProtein = target.isProtein;
	    proteinID = target.proteinID;
	    isTrigger = target.isTrigger;
	    triggerID = target.triggerID;
    }

    /**
     * retrieve original token of the node
     * including position number and POS tag
     * @return original token
     */
    public String getToken() {
    	return token;
    }

    /**
     * set the token of the node
     * this function is for newly split node
     * @param token
     */
    public void setToken(String token) {
    	this.token = token;
    }

    /**
     * retrieve the word of the node
     * @return word
     */
    public String getWord() {
    	return word;
    }

    /**
     * set the word of the node
     * this function is for newly split node
     * @param token
     */
    public void setWord(String word) {
    	this.word = word;
    }

    /**
     * retrieve the POS tag of the node
     * @return POS tag
     */
    public String getPOSTag() {
    	return tag;
    }

    /**
     * check if the graph node is a protein annotation or not
     * @return isProtein
     */
    public boolean isProtein() {
    	return isProtein;
    }

    /**
     * set isProtein field
     * @param isProtein
     */
    public void setIsProtein(boolean isProtein) {
    	this.isProtein = isProtein;
    }

    /**
     * set protein ID field
     * @param proteinID
     */
    public void setProteinID(String proteinID) {
    	this.proteinID = proteinID;
    }

    /**
     * retrieve protein ID associated with the node
     * @return protein ID
     */
    public String getProteinID() {
    	return proteinID;
    }

    /**
     * check if the graph node is a protein annotation or not
     * @return isArgument
     */
    public boolean isArgument() {
    	return isArgument;
    }

    /**
     * set isArgument field
     * @param isArgument
     */
    public void setIsArgument(boolean isArgument) {
    	this.isArgument = isArgument;
    }

    /**
     * set protein ID field
     * @param proteinID
     */
    public void setArgumentID(String argumentID) {
    	this.argumentID = argumentID;
    }

    /**
     * retrieve protein ID associated with the node
     * @return protein ID
     */
    public String getArgumentID() {
    	return argumentID;
    }

    /**
     * check if the graph node is a trigger annotation or not
     * @return isTrigger
     */
    public boolean isTrigger() {
    	return isTrigger;
    }

    /**
     * set isTrigger field
     * @param isTrigger
     */
    public void setIsTrigger(boolean isTrigger) {
    	this.isTrigger = isTrigger;
    }

    /**
     * set trigger ID field
     * @param triggerID
     */
    public void setTriggerID(String triggerID) {
    	this.triggerID = triggerID;
    }

    /**
     * retrieve trigger ID associated with the node
     * @return trigger ID
     */
    public String getTriggerID() {
    	return triggerID;
    }

    /**
     * set lemma for the node
     * @param lemma
     */
    public void setLemma(String lemma) {
    	this.lemma = lemma;
    }

    /**
     * retrieve the lemma of the node
     * @return lemma
     */
    public String getLemma() {
    	return lemma;
    }

    /**
     * retrieve the comparison form of the node
     * @return comparison form
     */
    public String getCompareForm() {
    	return compareForm;
    }

    /**
     * retrieve the token position of the node
     * @return token position
     */
    public int getTokenPosition() {
    	return pos;
    }

    /**
     * set the token position of the node
     * @param pos
     */
    public void setTokenPosition(int pos) {
    	this.pos = pos;
    }

    /**
     * retrieve the offset of the node
     * @return offset position relative to the entire document
     */
    public int getOffset() {
    	return offset;
    }

    /**
     * set the POS tag of the node
     * @param POS tag
     */
    public void setPOStag(String tag) {
    	this.tag = tag;
    }

    /**
     * set the offset of the node
     * @param offset
     */
    public void setOffset(int offset) {
    	this.offset = offset;
    }

    /**
     * set the corresponding PTB tree token of the node
     * @param treeToken
     */
    public void setTreeToken(Token treeToken) {
    	this.treeToken = treeToken;
    }

    /**
     * retrieve the corresponding PTB tree token of the node
     * @return tree token
     */
    public Token getTreeToken() {
    	return treeToken;
    }

    /**
     * set the comparison form of the node
     * @param compareForm
     */
    public void setCompareForm(String compareForm) {
    	this.compareForm = compareForm;
    }

    /**
     * set the generalized POS tag of the node
     * @param generalizedPOS
     */
    public void setGeneralizedPOS(String generalizedPOS) {
    	this.generalizedPOS = generalizedPOS;
    }

    /**
     * retrieve the generalized POS tag of the node
     * @return generalized POS tag
     */
    public String getGeneralizedPOS() {
    	return generalizedPOS;
    }

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + offset;
		result = prime * result + ((token == null) ? 0 : token.hashCode());
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
		Vertex other = (Vertex) obj;
		if (offset != other.offset)
			return false;
		if (token == null) {
			if (other.token != null)
				return false;
		} else if (!token.equals(other.token))
			return false;
		return true;
	}

	/**
	 * print node content
	 */
    @Override
	public String toString() {
		if(isProtein) {
			if (proteinID.length() == 0)
				LOG.error("Protein ID for '{}' has length 0", token);
			return BIO_ENTITY + proteinID + "-" + pos + "/" + tag;
		}
        else if (isArgument) {
            if (argumentID.length() == 0)
				LOG.error("Argument ID for '{}' has length 0", token);
			return ARG_PREFIX + word + argumentID + "-" + pos + "/" + tag;
        }
		return word + "-" + pos + "/" + tag;
	}
}
