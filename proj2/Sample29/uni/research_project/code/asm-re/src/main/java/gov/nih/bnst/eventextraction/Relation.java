package gov.nih.bnst.eventextraction;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import gov.nih.bnst.patternlearning.RelationRule;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

import edu.ucdenver.ccp.common.string.StringConstants;
import edu.uci.ics.jung.graph.DirectedGraph;

/**
 * Representation of a relation extracted from a
 * a dependency parse using an inferred rule.
 */
public class Relation {

	/** relationshipID in the A2 file */
	private int relationshipID = -1;

	/** relationship category */
	private String relationshipCategory;

	/** relationship themes, multiple for binding relationships */
	private Set<Vertex> relationshipThemes;

	/** original sentence dependency graph */
	private DirectedGraph<Vertex, Edge> sentenceGraph;

	/** original relationship rule */
	private RelationRule relationshipRule;

	/** associated relationship ids */
	Set<Integer> associatedRelationIDs;

	/** status used when generating A2 */
	boolean status = false;

    public Relation(RelationRule relationshipRule) {
        this.relationshipRule = relationshipRule;
        associatedRelationIDs = new HashSet<Integer>();
    }

    /**
     * use one relationship's information to update another relationship
     */
    public void update(Relation relationship) {
        relationshipCategory = relationship.relationshipCategory;
        relationshipThemes = relationship.relationshipThemes;
        sentenceGraph = relationship.sentenceGraph;
    }

	public String toA2String() {
		String a2Line = relationshipID + StringConstants.TAB + relationshipCategory;
		if (relationshipThemes != null) {
            int i = 1;
            for (Vertex theme : relationshipThemes) {
				a2Line += (" Arg" + i + ":" + theme.getProteinID());
                i += 1;
			}
		}
		return a2Line;
	}

	/**
     * print raw relationship content
     * Example: Positive_regulation:(Induction-1/NN) Theme:(Negative_regulation:inhibits-2/VBZ)
     */
    @Override
	public String toString(){
    	StringBuilder sb = new StringBuilder();
    	sb.append(relationshipCategory);

        //Relations do not have any triggers
        sb.append(":( ) ");

        //Add on the arguments
		List<Vertex> temp = new ArrayList<Vertex>(relationshipThemes);
		for(int i=0; i<temp.size(); i++) {
			sb.append("Arg" + (i+1) + ":(" + temp.get(i) + ") ");
		}

		return sb.toString();
    }

	public int getRelationID(){
		return relationshipID;
	}

	public boolean getStatus() {
		return status;
	}

	public void setStatus(boolean status) {
		this.status = status;
	}

	public Set<Integer> getAssociatedRelationIDs() {
		return associatedRelationIDs;
	}

	public void setRelationID(int relationshipID){
		this.relationshipID = relationshipID;
	}

	public String getRelationCategory(){
		return relationshipCategory;
	}

    public void setRelationCategory(String relationshipCategory) {
		this.relationshipCategory = relationshipCategory;
	}

	public Set<Vertex> getRelationThemes() {
		return relationshipThemes;
	}

	public void setRelationThemes(Set<Vertex> relationshipThemes) {
		this.relationshipThemes = relationshipThemes;
	}

    /**
     * check if the relationship has a theme
     */
    public boolean hasTheme() {
    	return relationshipThemes != null;
    }

    public void setSentenceGraph(DirectedGraph<Vertex, Edge> sentenceGraph) {
    	this.sentenceGraph = sentenceGraph;
    }

    public DirectedGraph<Vertex, Edge> getSentenceGraph() {
    	return sentenceGraph;
    }

    public RelationRule getOriginalRelationRule() {
    	return relationshipRule;
    }

    public void setOriginalRelationRule(RelationRule relationshipRule) {
    	this.relationshipRule = relationshipRule;
    }

    public static final String join(List<Vertex> c, String delimiter) {
		if (c.isEmpty()) {
			return "";
		}
		StringBuffer buffer = new StringBuffer(c.get(0).toString());
		for(int i=1; i<c.size(); i++) {
			buffer.append(delimiter).append(c.get(i).toString());
		}
		return buffer.toString();
	}

	@Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		result = prime * result
				+ ((relationshipCategory == null) ? 0 : relationshipCategory.hashCode());
		result = prime * result
				+ ((relationshipThemes == null) ? 0 : relationshipThemes.hashCode());
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
		Relation other = (Relation) obj;
		if (relationshipCategory == null) {
			if (other.relationshipCategory != null)
				return false;
		} else if (!relationshipCategory.equals(other.relationshipCategory))
			return false;
		if (relationshipThemes == null) {
			if (other.relationshipThemes != null)
				return false;
		} else if (!relationshipThemes.equals(other.relationshipThemes))
			return false;
		return true;
	}
}
