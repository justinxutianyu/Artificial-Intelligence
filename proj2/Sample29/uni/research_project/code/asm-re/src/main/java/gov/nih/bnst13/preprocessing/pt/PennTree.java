package gov.nih.bnst13.preprocessing.pt;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * <p>Information about Penntree Bank trees</p>
 * 
 */
public class PennTree {
	/** all tokens of the tree */
    private List<Token> tokens;
    
    /** Map to store token for easy token retrieval */
    private Map<String, Token> tokenMap;
    
    /** all noun phrases of the tree */
    private List<NounPhrase> nounPhrases;
    
    /** original string of the tree */
    private String tree;
    
    /** modified string of the tree, adding position information */
    private String modifiedTree;
	
    /**
	 * Construtor to initialize the class field
	 */
    public PennTree (String tree, List<Integer> offset) {
    	this.tree = tree;
    	modifiedTree = tree;
    	tokens = new ArrayList<Token>();
    	tokenMap = new HashMap<String, Token>();
    	nounPhrases = new ArrayList<NounPhrase>();
    	//adding position info into the original tree string
    	String[] array = tree.split("\\s+");
    	List<String> list = new ArrayList<String>();
    	int position = 1;
    	for(int i = 0; i< array.length; i++) { 
        	if(array[i].matches("^(\\S+?)(\\)+)$")) {
        		array[i] = ( array[i].replaceFirst("^(\\S+?)(\\)+)$", "$1-" + position + "$2") );
        		position++;
        	}
        	list.add(array[i]);
    	}	
    	/*
    	Pattern p = Pattern.compile("\\(([^\\(\\)]+?)\\s([^\\)\\(]+?)\\)");
		Matcher m = p.matcher(tree);
		//String rp = "\\(([^\\(\\)]+?)\\s([^\\)\\(\\-]+?)\\)";
		String rp = "\\(([^\\(\\)]+?)\\s([^\\)\\(\\-]+?)\\)";
		int position = 1;
		while(m.find()) { 
			modifiedTree = modifiedTree.replaceFirst(rp, "($1 $2-" + position + ")");
		    position++; 
		}*/
    	modifiedTree = join(list, " ");
		//System.out.println(modifiedTree);
		
    	//generate objects of tokens of the tree
		Pattern p = Pattern.compile("\\((\\S+?)\\s(\\S+?)\\)");
		Matcher m = p.matcher(modifiedTree);
		int count = 0;
		while(m.find()) { 
			Token t = new Token(m.group(1), m.group(2), offset.get(count++));
			tokens.add(t);
			tokenMap.put(m.group(2), t);
		}
		
		//generate objects of noun phrases of the tree
		List<String> npl = locateNounPhraseStrings(modifiedTree); //System.out.println(npl);
		//sort npl based on lenth of NPs from shortest to longest due to the existence of embeded NPs 
		//in order to solve the NP membership of tokens
		Collections.sort(npl, new MyComparator());
		for(String np : npl) { 
			NounPhrase n = new NounPhrase(np, tokenMap);
			for(Token t : n.getTokens())
				//if the token is already assigned a NP, don't touch it
				if(t.getNounPhrase() == null)
				    t.setNounPhrase(n); 
			//for(Token t : n.getTokens())
			//	System.out.println(t + " " + t.getNounPhrase());
			nounPhrases.add( n );
		}
    }
    
    /**
     * count the number of occurrences of a substring in a longer string
     * @param str : longer string
     * @param substr : substring to be checked
     * @return the occurrence count
     */
    private static int countSubstringMatches(String str, String substr) {
        int count = 0;
        int idx = 0;
        while ((idx = str.indexOf(substr, idx)) != -1) {
            count++;
            idx += substr.length();
        } 
        return count;
    }
    
    /**
     * recursively extract base Noun Phrases from PennTree Bank tree
     * Noun Phrases with embeded Noun Phrases will be also extracted if they satisfy criteria  
     * this method can be extended to extracting other types of phrases
     * @param original string of the tree
     * @return a list of noun phrases
     */
    private List<String> locateNounPhraseStrings(String tree) {
        //list of noun phrases
    	List<String> npl = new ArrayList<String>();
        //noun phrase
        List<String> np = new ArrayList<String>();
        String[] array = tree.split("\\s+");
        boolean flag = false;
        int leftBracket = 0;
        int rightBracket = 0;
        for(String s : array) { 
        	if(s.matches("^\\(NP$") && !flag) {
        		flag = true;
        		leftBracket++;
        		np.add(s);
        		continue;
        	}
        	if(s.startsWith("(") && flag) {
        		String temp = s;
        		temp = temp.substring(0, temp.length() - countSubstringMatches(s, ")") );
        		//added to fix cases like (NP (NN (.88-18))
        		if(!tokenMap.containsKey(temp)) {
        		    leftBracket = leftBracket + countSubstringMatches(s, "(");
        		    np.add(s); 
        		}    
        	}
        	if(s.endsWith(")") && flag) {
        		rightBracket = rightBracket + countSubstringMatches(s, ")");
        		np.add(s); 
        	} 
        	if( (leftBracket <= rightBracket) && flag ) {
        		String temp = join(np, " "); 
        		if(leftBracket < rightBracket) {
        			temp = temp.substring(0, temp.length() - (rightBracket - leftBracket) );
        		}
        		//recursively retrieve base noun phrases
        		if(countSubstringMatches(temp, "(NP") > 1) { 
        			//record the current NP with embeded NP(s) as long as there is no "(S ", "(VP " or "(PP "
        			if( (temp.indexOf("(S ") != -1) || (temp.indexOf("(VP ") != -1) 
        					|| (temp.indexOf("(PP ") != -1) ) {} //don't record; do nothing
        			else { npl.add(temp); }
        			//remove prefix "(NP " and suffix ")"
        			temp = temp.substring(4, temp.length() ); 
        			temp = temp.substring(0, temp.length() - 1 ); 
        			//update current npl list
        			npl.addAll( locateNounPhraseStrings(temp) );    	
        		}
        		else {
        			npl.add( temp );
        		}

        		flag = false;
        		leftBracket = 0;
        		rightBracket = 0;
        		np.clear();
        	}
        }
    	return npl;
    }
    
    /**
     * retrieve all tokens of the tree
     * @return tokens
     */
    public List<Token> getTokens() {
    	return tokens;
    }
    
    /**
     * retrieve original Penn tree string
     * @return tree string
     */
    public String getTreeString() {
    	return tree;
    }
    
    /**
     * retrieve mapping between surface tokens and tree tokens
     * @return tokenMap
     */
    public Map<String, Token> getTokenMap() {
    	return tokenMap;
    }
    
    /**
     * retrieve all noun phrases of the tree
     * @return nounPhrases
     */
    public List<NounPhrase> getNounPhrases() {
    	return nounPhrases;
    }
    
    /**
     * concatenate a collection of strings into one string using an input delimiter
     * @param s : a collection of strings
     * @param delimiter : delimiter to concatenate strings
     * @return a single concatenated string
     */
    private static String join( Collection<String> s, String delimiter) {
	    if (s.isEmpty()) return "";
	    Iterator<String> iter = s.iterator();
	    StringBuffer buffer = new StringBuffer(iter.next());
	    while (iter.hasNext()) buffer.append(delimiter).append(iter.next());
	    return buffer.toString();
	}
}

class MyComparator implements Comparator<String> {
    @Override
    public int compare(String o1, String o2) {  
      if (o1.length() > o2.length()) {
         return 1;
      } else if (o1.length() < o2.length()) {
         return -1;
      }
      return o1.compareTo(o2);
    }
}

