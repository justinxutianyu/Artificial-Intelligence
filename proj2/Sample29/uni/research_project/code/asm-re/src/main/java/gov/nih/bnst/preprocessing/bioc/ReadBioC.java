package gov.nih.bnst.preprocessing.bioc;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;


import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;
import gov.nih.bnst.sharedtask.bioc.Annotation;
import gov.nih.bnst.sharedtask.bioc.Collection;
import gov.nih.bnst.sharedtask.bioc.ConnectorWoodstox;
import gov.nih.bnst.sharedtask.bioc.Document;
import gov.nih.bnst.sharedtask.bioc.Passage;
import gov.nih.bnst.sharedtask.bioc.Sentence;


/**
 * modify the XML content
 * @author liuh11
 *
 */
public class ReadBioC {
	public static void main(String[] args) {
        String fileName = "bionlp-st-2013_ge_train_devel_texts_pos+lemma.xml";
        //generate bioc object to read BioC XML file
        ReadBioC bioC = new ReadBioC();        
        //read XML file
        //bioC.readXMLFile(fileName);
        bioC.writeOffsetsOfTokensInSentencesToFiles(fileName);
    }
 /* PMID-1377534.txt
    PMID-1439250.txt
	PMID-15510518.txt
	PMID-15723619.txt
	PMID-17016553.txt
	PMID-17305525.txt
	PMID-17981770.txt
	PMID-1821204.txt
	PMID-18537682.txt
	PMID-2418866.txt
	PMID-3759367.txt
	PMID-707591.txt
*/	
   
	public void writeTokenizedSentencesToFiles (String fileName) {
		ConnectorWoodstox inConnector = new ConnectorWoodstox();
    	printCollectionSourceName( inConnector.startRead("data/"+fileName) );
    	//specify where to write
		//set relative path
		String relativePath = "sentences/";
        while ( inConnector.hasNext() ) {
        	Document document = inConnector.next();
    		String outputFileName = relativePath + document.id.replaceFirst(".txt", ".formatted");
    		File outputFile = new File(outputFileName);
        	outputFile.getParentFile().mkdirs();
        	BufferedWriter output;
        	try {
    			output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8, 
                        WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
    		    //loop over the document
    			for(Passage passage : document.passages) {
    				if(passage.sentences.size() == 0)
    					continue;
    	            for(Sentence sentence : passage.sentences) { 
    	            	if(sentence.annotations.size() == 0)
    	            		continue;
    	            	List<String> tokens = new ArrayList<String>();
    	            	for(Annotation annotation : sentence.annotations) {
    	            	    tokens.add(annotation.text);	
    	            	}
    	            	output.write( "<s> " + join(tokens, " ") + " </s>\n" );
    	            } 
    			}    
    		    output.close();	
    		    System.out.println("Finish writing the file " + document.id); 
    		} catch (FileNotFoundException e) {
    			throw new RuntimeException("Unable to open the output file: "
    					+ outputFileName, e);
    		} catch (IOException e) {
    			throw new RuntimeException("Unable to process the output file: ", e);
    		} 
        }
	}
	
	public void writeOffsetsOfTokensInSentencesToFiles (String fileName) {
		ConnectorWoodstox inConnector = new ConnectorWoodstox();
    	printCollectionSourceName( inConnector.startRead("data/"+fileName) );
    	//specify where to write
		//set relative path
		String relativePath = "offsets/";
        while ( inConnector.hasNext() ) {
        	Document document = inConnector.next();
    		String outputFileName = relativePath + document.id.replaceFirst(".txt", ".offset");
    		File outputFile = new File(outputFileName);
        	outputFile.getParentFile().mkdirs();
        	BufferedWriter output;
        	try {
    			output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8, 
                        WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
    		    //loop over the document
    			for(Passage passage : document.passages) {
    				if(passage.sentences.size() == 0)
    					continue;
    	            for(Sentence sentence : passage.sentences) {
    	            	if(sentence.annotations.size() == 0)
    	            		continue;
    	            	List<String> offsets = new ArrayList<String>();
    	            	for(Annotation annotation : sentence.annotations) {
    	            	    if(annotation.text.length() == annotation.length)
    	            		    offsets.add(Integer.toString(annotation.offset));
    	            	    else
    	            	    	throw new RuntimeException("the length of annotation text "+ annotation.text + " is not " + annotation.length);
    	            	}
    	            	output.write( join(offsets, " ") +"\n" );
    	            } 
    			}    
    		    output.close();	
    		    System.out.println("Finish writing the file " + document.id); 
    		} catch (FileNotFoundException e) {
    			throw new RuntimeException("Unable to open the output file: "
    					+ outputFileName, e);
    		} catch (IOException e) {
    			throw new RuntimeException("Unable to process the output file: ", e);
    		} 
        }
	}
	
	
    public void readXMLFile( String fileName ){
    	ConnectorWoodstox inConnector = new ConnectorWoodstox();
    	printCollectionSourceName( inConnector.startRead("data/"+fileName) );
        while ( inConnector.hasNext() ) {
        	printDocumentContent( inConnector.next() );
        }
    }
    
    private void printCollectionSourceName(Collection collection) {
        System.out.println("Collection Source Name: " + collection.source);    	
    }	
    
    private void printDocumentContent(Document document) {
        System.out.println("File Name: " + document.id);
        for(Passage passage : document.passages)
            printPassageContent(passage);	
    }
    
    private void printPassageContent(Passage passage) {
        if(passage.sentences.size() == 0) {
            System.out.println("offset: " + passage.offset + " content: " + passage.text);	
        }
        else {
            for(Sentence sentence : passage.sentences)
        	    printSentenceContent(sentence);
            System.out.println("End of passage");
        }
    }
    
    private void printSentenceContent(Sentence sentence) {
    	if(sentence.annotations.size() == 0) {
            System.out.println("offset: " + sentence.offset + " content: " + sentence.text);	
        }
        else {
            for(Annotation annotation : sentence.annotations)
        	    printAnnotationContent(annotation);
            System.out.println("End of sentence");
        }	
    }
    
    private void printAnnotationContent(Annotation annotation) {
        String[] records = annotation.type.split("\\|");
        System.out.println("offset: " + annotation.offset);
        System.out.println("Token: " + annotation.text);
        System.out.println("POS: " + records[0]);
        System.out.println("Lemma: " + records[1]);
    }  
    
    /**
	 * static method to concatenate String items with a specified delimiter
	 * @param s
	 * @param delimiter
	 * @return concatenated String items with a specified delimiter
	 */
	private static String join(List<String> s, String delimiter) {
		if (s.isEmpty()) {
			return "";
		}
		Iterator<String> iter = s.iterator();
		StringBuffer buffer = new StringBuffer(iter.next());
		while (iter.hasNext()) {
			buffer.append(delimiter).append(iter.next());
		}
		return buffer.toString();
	}
}
