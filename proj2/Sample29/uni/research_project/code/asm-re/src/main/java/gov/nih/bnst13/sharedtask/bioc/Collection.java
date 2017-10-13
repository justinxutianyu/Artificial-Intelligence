package gov.nih.bnst13.sharedtask.bioc;

    
import java.util.ArrayList;


/**
 * Collection of documents.
 *
 * Collection of documents for a project. They may be an entire corpus
 * or some portion of a corpus. Fields are provided to describe the
 * collection.
 *
 * Documents may appear empty if doing document at a time IO.
 */
public class Collection {

    /**
       Describe the original source of the documents.
    */
    public String source;

    /**
       Date the documents obtained from the source.
    */
    public int date;

    /**
       Name of a file describing the contents and conventions used in
       this XML file.
    */
    public String key;

    /**
       All the documents in the collection. This will be empty of
    document at a time IO is used to read the XML file.
    */
    public ArrayList<Document> documents;

    public Collection() {
        source = new String();
        date = 0;
        key = new String();
        documents = new ArrayList<Document>();
    }
    public void write( ) {
        System.out.println("source: " + source);
        System.out.println("date: " + date );
        System.out.println("key: " + key );
        for( Document document: documents ) {
            document.write();
        }
    }

}
