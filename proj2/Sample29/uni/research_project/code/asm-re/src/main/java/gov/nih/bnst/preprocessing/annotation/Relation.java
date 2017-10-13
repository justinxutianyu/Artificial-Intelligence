package gov.nih.bnst.preprocessing.annotation;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import edu.ucdenver.ccp.common.string.StringConstants;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Relation {

    private static final Logger LOG = LoggerFactory.getLogger(Relation.class);

	/** original relation record in the ann file */
	private String relationRecord;

	/** relationID in the ann file that starts with capital letter R */
	private final String relationID;

	/** relation category */
	private final String relationCategory;

	/** relation themes */
	private List<String> relationThemes;

	/** sentenceID containing the relation */
	private Integer relationSentenceID = null;

	/** sentence text containing the relation */
	private String relationSentenceText = null;

    /**
	 * Constructor to directly use record line to initialize the class fields
	 *
	 * @param record
	 */
	public Relation(String record) {
        String[] id_rest = record.split("\t");
        this.relationID = id_rest[0];
        String[] category_args = id_rest[1].split(" ");
        this.relationCategory = category_args[0];
		this.relationThemes = new ArrayList<String>();
        this.relationThemes.add(category_args[1]);
        this.relationThemes.add(category_args[2]);
        LOG.info(
            "Matched relation with id {}, category {}, themes {}",
            relationID, relationCategory, relationThemes
        );
    }

	/**
	 * @param relationID
	 * @param relationCategory
	 * @param relationTrigger
	 * @param relationThemes
	 * @param relationCause
	 */
	public Relation(
        String relationID,
        String relationCategory
    ) {
		super();
		this.relationID = relationID;
		this.relationCategory = relationCategory;
		this.relationThemes = new ArrayList<String>();
	}

	public void addTheme(String themeId) {
		this.relationThemes.add(themeId);
	}

	public void setSentenceID(Integer relationSentenceID) {
		this.relationSentenceID = relationSentenceID;
	}

	public Integer getSentenceID() {
		return relationSentenceID;
	}

	public void setSentenceText(String relationSentenceText) {
		this.relationSentenceText = relationSentenceText;
	}

	public String getSentenceText() {
		return relationSentenceText;
	}

	public String toANNString() {
		String annLine =
            relationID
            + StringConstants.TAB
            + relationCategory;
		if (relationThemes != null) {
			int index = 1;
			for (String theme : relationThemes) {
				String label = "Arg" + index;
				annLine += (" " + label + ":" + theme);
				index++;
			}
		}
		return annLine;
	}

	public String getRelationID(){
		return relationID;
	}

	public String getRelationCategory(){
		return relationCategory;
	}

	public List<String> getRelationThemes(){
		return relationThemes;
	}
}
