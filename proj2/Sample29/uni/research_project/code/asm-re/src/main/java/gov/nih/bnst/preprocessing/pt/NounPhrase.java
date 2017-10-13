package gov.nih.bnst.preprocessing.pt;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * <p>Definition of "base" noun phrase for Penntree Bank trees</p>
 * 
 * <p>NounPhrase is then fed into objects of PennTree</p>
 * 
 */
public class NounPhrase {
	/** head token of the noun phrase */
    private Token headToken;
    
    /** all tokens contained in the noun phrase, maintained in an order of their natural occurrence in text */
    private List<Token> tokens;
	
    /** original textual surface form of the noun phrase */
    private String surfaceForm;
    
    /**
	 * Construtor to initialize the class field
	 */
    public NounPhrase (String np, Map<String, Token> tokenMap) { //System.out.println(np);
        tokens = new ArrayList<Token>();
    	Pattern p = Pattern.compile("\\((\\S+?)\\s(\\S+?)\\)");
		Matcher m = p.matcher(np);
		while(m.find()) {			
			tokens.add(tokenMap.get(m.group(2)));
		}
		//System.out.println(tokens);
		// check if the last element of the base noun is tagged as "NN.*"
		//if(tokens.size() > 1 && !tokens.get(tokens.size() - 1).getPOSTag().matches("^NN.*|CD|JJ$")) 
        //	throw new RuntimeException("The base noun phrase: "
		//			+ tokens.get(tokens.size() - 1) + "of" + tokens + " is not valid. Please check.");
		
		// head noun is specified as the last element of the base noun phrase
		headToken = tokens.get(tokens.size() - 1);
		for(Token t : tokens) {
			if(surfaceForm == null) surfaceForm = t.getWord();
			else surfaceForm = surfaceForm + " " + t.getWord();
		}
    }  
    
    /**
     * retrieve the surfact form of the noun phrase
     * @return surface form of the noun phrase
     */
    public String getNounPhrase() {
    	return surfaceForm;
    }
    
    /**
     * retrieve the tokens of the noun phrase
     * @return tokens of the noun phrase
     */
    public List<Token> getTokens() {
    	return tokens;
    }
    
    /**
     * retrieve the head token of the noun phrase
     * @return head token of the noun phrase
     */
    public Token getHeadToken() {
    	return headToken;
    }
    
    /**
	 * print the noun phrase
	 */
    @Override
	public String toString() {
		return surfaceForm;
	}
}


