package gov.nih.bnst13.sharedtask.bioc;



import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.util.Iterator;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLOutputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.XMLEvent;
import org.codehaus.stax2.XMLInputFactory2;
import org.codehaus.stax2.XMLStreamReader2;
import org.codehaus.stax2.XMLStreamWriter2;

/**
   Read and write BioC data using the woodstox StAX XML
   parser. Document at a time IO avoids using excessive memory.
*/
public class ConnectorWoodstox
    implements Iterator {
    boolean inDocument;
    boolean finishedXML;
    XMLStreamReader2 xmlr;

    /**
       Start reading XML file
       @param filename XML file to read
    */
    public Collection startRead( String filename ) {
	XMLInputFactory2 xmlif = null ;
	try{
            xmlif = (XMLInputFactory2)
		XMLInputFactory2.newInstance();
            xmlif.setProperty(
                              XMLInputFactory.
                              IS_REPLACING_ENTITY_REFERENCES,
                              Boolean.FALSE);
            xmlif.setProperty(
                              XMLInputFactory.
                              IS_SUPPORTING_EXTERNAL_ENTITIES,
                              Boolean.FALSE);
            xmlif.setProperty(
                              XMLInputFactory.
                              IS_COALESCING,
                              Boolean.FALSE);
            xmlif.configureForSpeed();
        }catch(Exception ex){
            ex.printStackTrace();
        }

        Collection collection = new Collection();
        
        try{
            xmlr =
		(XMLStreamReader2)
		xmlif.createXMLStreamReader(
                                            filename, new
                                            FileInputStream(filename));
            int eventType = xmlr.getEventType();
            String curElement = "";
            finishedXML = false;
            inDocument = false;

            while(xmlr.hasNext() && ! inDocument ){
		eventType = xmlr.next();
		switch (eventType) {
                case XMLEvent.START_ELEMENT:
                    curElement = xmlr.getName().toString();
                    if ( curElement.equals( "document" ) )
                        inDocument = true;
                    else if ( curElement.equals( "source" ) )
                        collection.source = getString("source");
                    else if ( curElement.equals( "date" ) )
                        collection.date = getInt( "date" );
                    else if ( curElement.equals( "key" ) )
                        collection.key = getString( "key" );
                    break;
                case XMLEvent.END_ELEMENT:
                    if ( curElement.equals( "collection" ) ) {
                        inDocument = false;
                        finishedXML = true;
                    }
                    break;
                case XMLEvent.END_DOCUMENT:
                    inDocument = false;
                    finishedXML = true;
                    break;
                }
            }
        }
        catch(XMLStreamException ex){
            System.out.println( ex.getMessage());
            if(ex.getNestedException() != null) {
		ex.getNestedException().
                    printStackTrace();
            }
        }
        catch(Exception ex){
            ex.printStackTrace();
        }
        
        return collection;
    }

    /**
       Returns true if the collection has more documents.
    */
    public boolean hasNext() {
        if ( finishedXML )
            return false;
        if ( inDocument )
            return true;

        try {
            while(xmlr.hasNext()){
                int eventType = xmlr.next();
                switch (eventType) {
                case XMLEvent.START_ELEMENT:
                    if ( xmlr.getName().toString().equals("document") ) {
                        inDocument = true;
                        return true;
                    }
                    break;
                case XMLEvent.END_DOCUMENT:
                    finishedXML = true;
                    inDocument = false;
                    return false;
                }
            }
        }
        catch(XMLStreamException ex){
            System.out.println( ex.getMessage());
            if(ex.getNestedException() != null) {
		ex.getNestedException().
                    printStackTrace();
            }
        }
        
        // end of XML
        finishedXML = true;
        inDocument = false;
        return false;
    }

    /**
       Returns the document in the collection.
    */
    public Document next() {
        Document document = new Document();
        try {
            if ( finishedXML )
                return null;
            if ( ! inDocument ) {
                if ( ! hasNext() )
                    return null;
                if ( ! inDocument )
                    throw new XMLStreamException("*** impossible after hasNext() true; inDocument false");
            }
            
            fromXML(document);
        }
        catch(XMLStreamException ex){
            System.out.println( ex.getMessage());
            if(ex.getNestedException() != null) {
		ex.getNestedException().printStackTrace();
            }
        }
        catch(Exception ex){
            ex.printStackTrace();
        }
        return document;
    }


    void fromXML( Document document ) throws XMLStreamException {
        while ( xmlr.hasNext() ) {
            int eventType = xmlr.next();
            switch (eventType) {
            case XMLEvent.START_ELEMENT:
                String name = xmlr.getName().toString();
                if ( name.equals("id") )
                    document.id = getString( "id" );
                else if ( name.equals("passage") )
                    document.passages.add( getPassage() );
                break;
            case XMLEvent.END_ELEMENT:
                if( xmlr.getName().toString().equals("document") )
                    inDocument = false;
                return;
            }
        }
    }
    
    String getString( String name ) throws XMLStreamException {

        StringBuilder buf = new StringBuilder();
        while ( xmlr.hasNext() ) {
            int eventType = xmlr.next();
            switch (eventType) {
            case XMLEvent.CHARACTERS:
                buf.append( xmlr.getText() );
                break;
            case XMLEvent.END_ELEMENT:
                if ( xmlr.getName().toString().equals(name) ) {
                    return buf.toString();
                }
            }
        }
        
        return "";              // should NOT be here
    }
    
    Passage getPassage() throws XMLStreamException {
        
        Passage passage = new Passage();
        while ( xmlr.hasNext() ) {
            int eventType = xmlr.next();
            switch (eventType) {
            case XMLEvent.START_ELEMENT:
                String name = xmlr.getName().toString();
                if ( name.equals("type") )
                    passage.type = getString( "type" );
                else if ( name.equals("offset") )
                    passage.offset = getInt( "offset" );
                else if ( name.equals("text") )
                    passage.text = getString( "text" );
                else if ( name.equals("sentence") )
                    passage.sentences.add( getSentence() );
                else if ( name.equals("annotation") )
                    passage.annotations.add( getAnnotation() );
                else if ( name.equals("relation") )
                    passage.relations.add( getRelation() );
                break;
            case XMLEvent.END_ELEMENT:
                if( xmlr.getName().toString().equals("passage") )
                    return passage;
                throw new XMLStreamException("found at end of passage: " +
                                             xmlr.getName().toString() );
            }
        }
        return passage;
    }
    
    Sentence getSentence() throws XMLStreamException {
        
        Sentence sentence = new Sentence();
        
        while ( xmlr.hasNext() ) {
            int eventType = xmlr.next();
            switch (eventType) {
            case XMLEvent.START_ELEMENT:
                String name = xmlr.getName().toString();
                if ( name.equals("offset") )
                    sentence.offset = getInt( "offset" );
                else if ( name.equals("text") )
                    sentence.text = getString( "text" );
                else if ( name.equals("annotation") )
                    sentence.annotations.add( getAnnotation() );
                else if ( name.equals("relation") )
                    sentence.relations.add( getRelation() );
                break;
            case XMLEvent.END_ELEMENT:
                if( xmlr.getName().toString().equals("sentence") )
                    return sentence;
                throw new XMLStreamException("found at end of sentence: " +
                                             xmlr.getName().toString() );
            }
        }
        return sentence;
    }
    
    Annotation getAnnotation() throws XMLStreamException {
        
        Annotation annotation = new Annotation();
        
        String id = xmlr.getAttributeValue( null, "id" );
        if ( id != null )
            annotation.id = id;
        
        while ( xmlr.hasNext() ) {
            int eventType = xmlr.next();
            switch (eventType) {
            case XMLEvent.START_ELEMENT:
                String name = xmlr.getName().toString();
                if ( name.equals("type") )
                    annotation.type = getString( "type" );
                if ( name.equals("offset") )
                    annotation.offset = getInt( "offset" );
                if ( name.equals("length") )
                    annotation.length = getInt( "length" );
                else if ( name.equals("text") )
                    annotation.text = getString( "text" );
                break;
            case XMLEvent.END_ELEMENT:
                if( xmlr.getName().toString().equals("annotation") )
                    return annotation;
                throw new XMLStreamException( "found at end of annotation: " +
                                              xmlr.getName().toString() );
            }
        }
        return annotation;
    }
    
    Relation getRelation() throws XMLStreamException {
        
        Relation relation = new Relation();
        
        String id = xmlr.getAttributeValue( null, "id" );
        if ( id != null )
            relation.id = id;
        
        while ( xmlr.hasNext() ) {
            int eventType = xmlr.next();
            switch (eventType) {
            case XMLEvent.START_ELEMENT:
                String name = xmlr.getName().toString();
                if ( name.equals("type") )
                    relation.type = getString( "type" );
                else if ( name.equals("label") )
                    relation.labels.add( getString("label") );
                else if ( name.equals("ref_id") )
                    relation.ref_ids.add( getString("ref_id") );
                break;
            case XMLEvent.END_ELEMENT:
                if( xmlr.getName().toString().equals("relation") )
                    return relation;
                throw new XMLStreamException("found at end of relation: " +
                                             xmlr.getName().toString() );
            }
        }
        return relation;
    }
    

    int getInt( String name ) throws XMLStreamException {
        String strValue = getString( name );
        return Integer.parseInt( strValue );
    }


    XMLStreamWriter2 xtw = null;

    /**
       Starting writing an XML document.

       @param filename   name of the XML file to write
       @param collection collection to write
       @param dtd        DTD that describes data written
    
       Since this class is for document at a time IO, any documents in
       the collection are ignored.
    */
    public void startWrite(String filename, Collection collection,
                            String dtd ) {
        try {
            // ?? if filename == '-', write to Print.out ??
            XMLOutputFactory xof =XMLOutputFactory.newInstance();
            xtw = null;
            xtw = (XMLStreamWriter2)
                xof.createXMLStreamWriter(
                                          new FileOutputStream(filename));
            //                                      new FileWriter(filename));

            //            xtw.writeStartDocument(null,"1.0");
            xtw.writeStartDocument();
            xtw.writeDTD("collection", dtd, null, null);
            xtw.writeStartElement("collection");
            writeXML("source", collection.source);
            writeXML("date", collection.date);
            writeXML("key", collection.key);
        }
        catch ( Exception ex ) {
            System.err.println("Exception occured while writing " + ex);
            ex.printStackTrace();
        }
    }

    /**
       Call after last document has been written.
       Performs any needed cleanup and closes the XML file.
    */
    public void endWrite() {
        try {
            xtw.writeEndElement();
            xtw.writeEndDocument();
            xtw.flush();
            xtw.close();
        }
        catch ( Exception ex ) {
            System.err.println("Exception occured while writing " + ex);
            ex.printStackTrace();
        }
    }

    /**
       Write the next document to the XML file.
       @param document document to write
    */
    public void writeNext( Document document ) {
        try {
            writeXML( document );
        }
        catch ( Exception ex ) {
            System.err.println("Exception occured while writing " + ex);
            ex.printStackTrace();
        }
    }
    
    void writeXML( Document document ) throws XMLStreamException {
        xtw.writeStartElement("document");
        writeXML("id", document.id );
        for ( Passage passage : document.passages )
            writeXML(passage);
        xtw.writeEndElement();
    }

    void writeXML( Passage passage ) throws XMLStreamException {
        xtw.writeStartElement("passage");
        writeXML("type", passage.type );
        writeXML("offset", passage.offset );
        if ( passage.text.length() > 0 )
            writeXML("text", passage.text );
        for ( Sentence sentence : passage.sentences )
            writeXML( sentence );
        for ( Annotation annotation : passage.annotations )
            writeXML( annotation );
        for ( Relation relation : passage.relations )
            writeXML( relation );
        xtw.writeEndElement();
    }

    void writeXML( Sentence sentence ) throws XMLStreamException {
        xtw.writeStartElement("sentence");
        writeXML("offset", sentence.offset );
        if ( sentence.text.length() > 0 )
            writeXML("text", sentence.text );
        for ( Annotation annotation : sentence.annotations )
            writeXML( annotation );
        for ( Relation relation : sentence.relations )
            writeXML( relation );
        xtw.writeEndElement();
    }

    void writeXML( Annotation annotation ) throws XMLStreamException {
        xtw.writeStartElement("annotation");
        if ( annotation.id.length() > 0 )
            xtw.writeAttribute("id", annotation.id );
        writeXML("type", annotation.type );
        writeXML("offset", annotation.offset );
        writeXML("length", annotation.length );
        writeXML("text", annotation.text );
        xtw.writeEndElement();
    }
        

    void writeXML( Relation relation ) throws XMLStreamException {
        xtw.writeStartElement("relation");
        if ( relation.id.length() > 0 )
            xtw.writeAttribute("id", relation.id );
        writeXML("type", relation.type );
        for ( String label : relation.labels )
            writeXML( "label", label );
        for ( String ref_id : relation.ref_ids )
            writeXML( "ref_id", ref_id );
        xtw.writeEndElement();
    }

    void writeXML( String element, String contents ) throws XMLStreamException {
        xtw.writeStartElement(element);
        xtw.writeCharacters(contents);
        xtw.writeEndElement();
    }

    void writeXML( String element, int contents ) throws XMLStreamException {
        writeXML(element, new Integer(contents).toString() );
    }

    public void remove(){
        throw new UnsupportedOperationException();
    }
}
