/**

 */
package gov.nih.bnst.preprocessing.annotation;

import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


import edu.ucdenver.ccp.common.string.StringConstants;
import gov.nih.bnst.preprocessing.dp.Vertex;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * class that generates an event argument object
 */
public class Argument {

	private static final Logger LOG  = LoggerFactory.getLogger(Trigger.class);

	/** original argument record in the A2 file */
	private final String argumentRecord;

	/** argumentID in the A2 file that starts with capital letter T */
	private final String argumentID;

	/** argument category */
	private final String argumentCategory;

	/** specific argument name */
	private final String argumentName;

	/** the start index of the argument */
	private final int startIndex;

	/**
	 * according to the definition in BioNLP09, the endIndex is the startIndex +
	 * length(triggerName), and corresponds to the index of the next byte
	 */
	private final int endIndex;

	/** corresponding dependency graph nodes of the argument */
	private Vertex graphNode;

	/** centerNode of the argument nodes */
	private Vertex centerNode;

	/**
	 * @param triggerID
	 * @param triggerCategory
	 * @param triggerName
	 * @param startIndex
	 * @param endIndex
	 */
	public Argument(String argumentID, String argumentCategory, String argumentName, int startIndex, int endIndex) {
		super();
		this.argumentID = argumentID;
		this.argumentCategory = argumentCategory;
		this.argumentName = argumentName;
		this.startIndex = startIndex;
		this.endIndex = endIndex;
		this.argumentRecord = argumentID + StringConstants.TAB + argumentCategory + StringConstants.SPACE + startIndex
				+ StringConstants.SPACE + endIndex + StringConstants.TAB + argumentName;
	}

	public String toA2String() {
		return argumentRecord;
	}

	public String getArgumentID(){
		return argumentID;
	}

	public String getArgumentName(){
		return argumentName;
	}

	public String getArgumentCategory(){
		return argumentCategory;
	}

	public String getArgumentSpan(){
		return Integer.toString(startIndex) + "-" + Integer.toString(endIndex-1);
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
