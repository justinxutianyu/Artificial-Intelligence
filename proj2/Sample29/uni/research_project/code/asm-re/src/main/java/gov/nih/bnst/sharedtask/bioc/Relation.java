package gov.nih.bnst.sharedtask.bioc;


import java.util.ArrayList;

/**
   Relationship between multiple {@link Annotation}s and possibly
   other {@code Relation}s.
 */
public class Relation {

    /**
       Used to refer to this relation in other relationships.
    */
    public String id;

    /**
       Type of relation. Implemented examples include abbreviation
       long forms and short forms and protein events.
    */
    public String type;

    /**
       Describes how the referenced annotated object or other
       relation participates in the current relationship.
     */
    public ArrayList<String> labels;

    /**
        Id of an annotated object or another relation. Typically
        there will be one label for each ref_id.

        Better Java names would be refId and refIds. The chosen values
        match the names in XML representation.
    */
    public ArrayList<String> ref_ids;  // id of Relation or Annotation

    public Relation() {
        id = "";
        type = "";
        labels = new ArrayList<String>();
        ref_ids = new ArrayList<String>();
    }

    public void write() {
        System.out.println("id: " + id);
        System.out.println("type: " + type);
        for ( String label : labels ) {
            System.out.println("label: " + label);
        }
        for ( String ref_id : ref_ids ) {
            System.out.println("ref id: " + ref_id );
        }
    }
}
