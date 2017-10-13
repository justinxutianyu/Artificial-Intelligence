package gov.nih.bnst.sharedtask.bioc;


import java.util.ArrayList;

/**
   Each {@code Document} in the {@link Collection}.

   An id, typically from the original corpus, identifies the
   particular document.
*/
public class Document {

    /**
       Id to identify the particular {@code Document}.
    */
    public String id;

    /**
       List of passages that comprise the document.

       For PubMed references, they might be "title" and
       "abstract". For full text papers, they might be Introduction,
       Methods, Results, and Conclusions. Or they might be paragraphs.
    */
    public ArrayList<Passage> passages;

    public Document() {
        id = "";
        passages = new ArrayList<Passage>();
    }
    public void write() {
        System.out.println("id: " + id );
        for ( Passage passage : passages )
            passage.write();
    }
}
