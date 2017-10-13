package gov.nih.bnst13.preprocessing.pt;

import gov.nih.bnst13.preprocessing.dp.Vertex;

import java.util.regex.Matcher;
import java.util.regex.Pattern;


/**
 * <p>Definition of token for Penntree Bank trees</p>
 * 
 * <p>Token is then fed into objects of PennTree</p>
 * 
 */
public class Token {
	/** original entire token including position number */
    private String token;
    
    /** sentence token only */
    private String word;
    
    /** POS tag */
    private String tag;
    
    /** lemma of word */
    private String lemma;
    
    /** token position */
    private int pos;
    
    /** offset position relative to the entire document */
    private int offset;
    
    /** for quick node comparison */
    private String compareForm;
    
    /** corresponding dependency graph node */
    private Vertex graphNode;
    
    /** membership of a base noun phrase */
    private NounPhrase nounPhrase;
    
    /**
	 * Construtor to initialize the class field
	 */
    public Token (String tag, String token, int offset) {
        this.tag = tag;
        this.token = token;
        Matcher m = Pattern.compile("^(.+)-(\\d+)$").matcher(token);	
        if(!m.find()) 
        	throw new RuntimeException("The token: "
					+ token + " is not valid. Please check.");
	    word = m.group(1);
	    pos = Integer.parseInt(m.group(2));
	    this.offset = offset;
    }  
    
    /**
	 * default Construtor to initialize the class fields to empty
	 */
    public Token () {
	    lemma = "";
    	//defaulted position -1 as 0 is taken by ROOT 
	    pos = -1;
	    tag = "";
	    token = "";
    }  
    
    /**
     * retrieve original token
     * @return original token 
     */
    public String getToken() {
    	return token;
    }
    
    /**
     * retrieve word of the token
     * @return token word
     */
    public String getWord() {
    	return word;
    }
    
    /**
     * retrieve the POS tag of the token
     * @return POS tag
     */
    public String getPOSTag() {
    	return tag;
    }
    
    /**
     * retrieve the position of the token
     * @return token position relative to the sentence
     */
    public int getTokenPosition() {
    	return pos;
    }
    
    /**
     * retrieve the offset of the token
     * @return offset position relative to the entire document
     */
    public int getOffset() {
    	return offset;
    }
    
    /**
     * retrieve the base noun phrase which the token belong to
     * @return noun phrase
     */
    public NounPhrase getNounPhrase() {
    	return nounPhrase;
    }
    
    /**
     * set the base noun phrase which the token belong to
     */
    public void setNounPhrase(NounPhrase np) {
    	nounPhrase = np;
    }
    
    @Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result + ((tag == null) ? 0 : tag.hashCode());
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
		Token other = (Token) obj;
		if (tag == null) {
			if (other.tag != null)
				return false;
		} else if (!tag.equals(other.tag))
			return false;
		if (token == null) {
			if (other.token != null)
				return false;
		} else if (!token.equals(other.token))
			return false;
		return true;
	}
	
	/**
     * set lemma for the token
     * @param lemma
     */
    public void setLemma(String lemma) {
    	this.lemma = lemma;
    }
    
    /**
     * retrieve the lemma of the token
     * @return lemma
     */
    public String getLemma() {
    	return lemma;
    }
    
	/**
     * set the corresponding dependency graph node of the token
     * @param graph node
     */
    public void setGraphNode(Vertex graphNode) {
    	this.graphNode = graphNode;
    }
    
    /**
     * retrieve the corresponding dependency graph node of the token
     * @return graph node
     */
    public Vertex getGraphNode() {
    	return graphNode;
    }
    
    /**
     * retrieve the comparison form of the token
     * @return comparison form
     */
    public String getCompareForm() {
    	return compareForm;
    }
    
    /**
     * set the comparison form of the token
     * @param compareForm
     */
    public void setCompareForm(String compareForm) {
    	this.compareForm = compareForm;
    }

	/**
     * print token content
     */
    @Override
	public String toString(){
		return token + "/" + tag;
    }
    
}
