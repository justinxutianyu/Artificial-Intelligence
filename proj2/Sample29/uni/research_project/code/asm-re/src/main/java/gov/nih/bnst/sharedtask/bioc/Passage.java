package gov.nih.bnst.sharedtask.bioc;


import java.io.OutputStreamWriter;
import java.io.Writer;
import java.util.ArrayList;

/**
   One passage in a {@link Document}.

   This might be the {@code text} in the passage. It could be the
   {@link Sentence}s in the passage. Or it might be {@link
   Annotation}s and possibly {@link Relation}s on the text of the
   passage.

   There is no code to keep those possibilities mutually exclusive.
   However the currently available DTDs only describe the listed
   possibilities
*/
public class Passage {

    /**
       Type of text in the passage.
       
       For PubMed references, it might be "title" or "abstract". For
       full text papers, it might be Introduction, Methods, Results,
       or Conclusions. Or they might be paragraphs.
    */
    public String type;

    /**
       The offset of the passage in the parent document. The
       significance of the exact value may depend on the source
       corpus. They should be sequential and identify the passage's
       position in the document.  Since pubmed is extracted from an
       XML file, the title has an offset of zero, while the abstract
       is assumed to begin after the title and one space.
     */
    public int offset;

    /**
       The orginal text of the passage.
    */
    public String text;

    /**
       The sentences of the passage.
    */
    public ArrayList<Sentence> sentences;

    /**
       Annotations on the text of the passage.
    */
    public ArrayList<Annotation> annotations;

    /**
       Relations between the annotations and possibly other relations
       on the text of the passage.
    */
    public ArrayList<Relation> relations;

    public Passage() {
        type = "";
        offset = 0;
        text = "";
        sentences = new ArrayList<Sentence>();
        annotations = new ArrayList<Annotation>();
        relations = new ArrayList<Relation>();
    }

    public void write() {
        try {
            Writer w = new OutputStreamWriter( System.out, "UTF-8" );
            System.out.println("type: " + type );
            System.out.println("offset: " + offset);
            if ( text.length() > 0 ) {
                System.out.print("text: ");
                w.write(text); w.flush();
                System.out.println();
            }
            for ( Sentence sentence : sentences )
                sentence.write();
            for ( Annotation annotation : annotations )
                annotation.write();
            for ( Relation relation : relations )
                relation.write();
        }
        catch (Exception ex) {
            System.out.println( "problem in passage write: " + ex );
        }
    }
}
