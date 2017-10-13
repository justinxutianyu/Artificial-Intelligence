package gov.nih.bnst13.sharedtask.bioc;


import java.util.ArrayList;

/**
   One sentence in a {@link Passage}.

   It may contain the original text of the sentence or it might be
   {@link Annotation}s and possibly {@link Relation}s on the text of
   the passage.

   There is no code to keep those possibilities mutually exclusive.
   However the currently available DTDs only describe the listed
   possibilities
*/
public class Sentence {
    /**
       A {@code Document} offset to where the sentence begins in the
       {@code Passage}. This value is the sum of the passage offset
       and the local offset within the passage.
    */
    public int offset;

    /**
       The original text of the sentence.
    */
    public String text;

    /**
       {@link Annotation}s on the original text
    */
    public ArrayList<Annotation> annotations;
    
    /**
       Relations between the annotations and possibly other relations
       on the text of the sentence.
    */
    public ArrayList<Relation> relations;

    public Sentence() {
        offset = 0;
        text = "";
        annotations = new ArrayList<Annotation>();
        relations = new ArrayList<Relation>();
    }

    public void write() {
        System.out.println("offset: " + offset );
        if ( text.length() > 0 )
            System.out.println("text: " + text);
        for ( Annotation annotation : annotations )
            annotation.write();
        for ( Relation relation : relations )
            relation.write();
    }
}
