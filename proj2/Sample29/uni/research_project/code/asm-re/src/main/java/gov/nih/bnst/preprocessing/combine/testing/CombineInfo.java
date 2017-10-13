package gov.nih.bnst.preprocessing.combine.testing;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Set;

import org.apache.log4j.Level;
import org.apache.log4j.Logger;

import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.reader.StreamLineIterator;
import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst.preprocessing.dp.*;
import gov.nih.bnst.preprocessing.annotation.*;
import gov.nih.bnst.preprocessing.combine.training.AnnotatedSentence;
import gov.nih.bnst.preprocessing.combine.training.ReadSingleSentenceOutput;

/**
 * <p>Combining all related information for training data</p>
 * 
 * @author Implemented and tested by Haibin Liu
 *
 */
public class CombineInfo {
	/** path to the syntax tree directory */
	private static final String PATH_TO_TREE = "resources/test_sentences/ParseTree_result_GE_McClosky";
	/** path to the dependency graph directory of McClosky_Charniak parser */
	private static final String PATH_TO_GRAPH_MCCLOSKY = "resources/test_sentences/ParseGraph_result_GE_McClosky";
	/** path to the offset directory */
	private static final String PATH_TO_OFFSET = "resources/test_sentences/offset_GE";
	/** path to the gold annotation directory including A1 and A2 files */
	private static final String PATH_TO_ANNOTATION = "resources/test_sentences/annotation_GE";
	/** the logger for suppressing the logger warning in StreamLineIterator*/
	private static final Logger logger = Logger.getLogger(CombineInfo.class);
	/** store all documents of the directory*/
	Map<String, List<AnnotatedSentence>> documents = new HashMap<String, List<AnnotatedSentence>>();
	/** store the last protein ID in each document for indexing triggers in later process */
	Map<String, Integer> lastProteinIDOfEachDocument = new HashMap<String, Integer>();
	/** graph type to be retrieved: M stands for McClosky; S stands for Stanford */
	String graphType;
	
	/**
	 * Constructor to process all files in the task directory
	 */
	public CombineInfo (String graphType) {
		logger.getRootLogger().setLevel(Level.OFF);	
		this.graphType = graphType;
		//read shared task directory and process each file in it
	    processSharedTaskDirectory();	
	}
	
	/**
	 * process the shared task file directory
	 */
	public void processSharedTaskDirectory() {
		File directory = new File(PATH_TO_TREE);
		if (!directory.isDirectory()) {
			throw new RuntimeException("The provided diretory: " + directory.getAbsolutePath()
					+ " is not a directory. Please check.");
		}
		int fileCount = 0;
		for (File inputFile : directory.listFiles()) {
			if (!inputFile.isFile() || !inputFile.getName().matches("^\\S+\\.(pstree)$")) {
				continue;
			} 
			//if(!inputFile.getName().equals("PMC-2222968-00-TIAB.pstree")) continue;
			File treeFile = inputFile;
			//get the pmid
			String pmid = treeFile.getName().split("\\.")[0];
			File graphFileMcClosky = new File(PATH_TO_GRAPH_MCCLOSKY, pmid + ".dep");
			File offsetFile = new File(PATH_TO_OFFSET, pmid + ".offset");
			if (!graphFileMcClosky.exists() || !offsetFile.exists()) {
				throw new RuntimeException("Detected tree file missing corresponding graph file or offset file: " + treeFile.getAbsolutePath());
			}
			//System.out.println("processing ...... " + pmid + " the " + ++fileCount + " file.");
			List<AnnotatedSentence> document = processSingleDocument(treeFile, graphFileMcClosky, offsetFile);
			//reading and processing annotation files: a1 and a2
			try{ 
			    File a1File = new File(PATH_TO_ANNOTATION, pmid + ".a1");
			    //mapping from ProteinID to protein
			    Map<String, Protein> proteinId2ProteinMap = readA1File(a1File);
				
				for(AnnotatedSentence sentence : document) {
					//System.out.println("sentence " + sentence.getSentenceID() + " " + sentence.getStartIndex() + " " + sentence.getEndIndex());
					//associate gold annotations with each sentence, only about protein, trigger and event
					associateGoldAnnotationWithEachSentence(sentence, proteinId2ProteinMap);
					//associate sentence gold annotation with dependency graph
					associateSentenceGoldAnnotationWithDependencyGraph(sentence, graphType);
					/*// check the existence of special case: trigger and theme are in the same node 
					if(sentence.getProteins() != null)
					    for(String protein : sentence.getProteins().keySet()) {
						    Vertex p = sentence.getProteins().get(protein).getGraphNode();
						    if(sentence.getTriggers() != null)
							    for(String trigger : sentence.getTriggers().keySet()) {
							    	Set<Vertex> v = sentence.getTriggers().get(trigger).getTriggerNodes();
							    	if(v.contains(p)) {
                                        System.out.println(protein + " " + trigger + " " + p);	System.exit(1);
							    	}    
							    }
					    }*/
				}
			}catch(IOException e) {
			    e.printStackTrace();
			    System.out.println(e.getMessage());
		    }
			documents.put(pmid, document);
		}	
	}
	
	/**
	 * associate provided gold annotation with each sentence
	 * @param sentence: the specific sentence
	 * @param proteinId2ProteinMap: document-level mapping from protein id to protein
	 * @param triggerId2TriggerMap: document-level mapping from trigger id to trigger
	 * @param eventId2EventMap: document-level mapping from event id to event
	 * @param anaphoraId2AnaphoraMap: document-level mapping from anaphora id to anaphora
	 * @param coreferenceId2CoreferenceMap: document-level mapping from coreference id to coreference
	 */
	private void associateGoldAnnotationWithEachSentence(AnnotatedSentence sentence, Map<String, Protein> proteinId2ProteinMap) {
		Map<String, Protein> proteins = new HashMap<String, Protein>();
		for(Protein protein : proteinId2ProteinMap.values()) {
			if( (protein.getStartIndex() >= sentence.getStartIndex()) && 
					( (protein.getEndIndex() < sentence.getEndIndex()) || (sentence.getEndIndex() == -1) ) ) {
				proteins.put(protein.getProteinID(), protein);
			}
		}
		if(proteins.size() != 0)
		    sentence.setProteins(proteins);
	}
	
	/**
	 * associate sentence gold annotation (proteins and triggers) with dependency graph
	 * @param sentence
	 */
	private void associateSentenceGoldAnnotationWithDependencyGraph(AnnotatedSentence sentence, String graphType) {
	    //if no annotation, directly return
		if(sentence.getProteins() == null) return;
		//associate proteins
		for(String proteinID : sentence.getProteins().keySet()) {
			Protein protein = sentence.getProteins().get(proteinID);
			Set<Vertex> graphNodes = new HashSet<Vertex>();
			graphNodes = 
	        	searchGraphNodeForAnnotationToken(protein.getStartIndex(), protein.getEndIndex(), sentence.getDependencyGraph().getGraph());
	        Vertex centerNode = null;
	        if(graphNodes.size() != 0) {
	        	//choose the center protein node in order to keep only one graph node for each protein annotation
				centerNode = searchCenterNodeForAnnotationGraphNodes(graphNodes, sentence);
	        	if(centerNode == null) { throw new RuntimeException("There is no center node found for " + graphNodes); }
				//update protein vertex lemma to "BIO_Entity"
	        	//split node for special case: trigger and theme are in the same node, normally separated by "-" in the node
	        	if(centerNode.getWord().length() != protein.getProteinName().length()) {
	        	    String candidate = centerNode.getWord();
	        	    //first replace protein with "BIO_Entity" in the String
	        	    if(centerNode.getWord().length() > protein.getProteinName().length())
	        	        candidate = candidate.replaceFirst(protein.getProteinName(), "BIO_Entity");
	        	    else if(centerNode.getOffset() < protein.getEndIndex()) {
	        	    	StringBuffer buffer = new StringBuffer(candidate);
	        	    	int start = 0;
	        	        int end = protein.getEndIndex() - centerNode.getOffset();
	        	        buffer.replace(start, end, "BIO_Entity");
	        	        candidate = buffer.toString(); 
	        	    }	
	        	    else if(centerNode.getOffset() + centerNode.getWord().length() > protein.getStartIndex()) {
	        	    	StringBuffer buffer = new StringBuffer(candidate);
	        	    	int start = protein.getStartIndex() - centerNode.getOffset();
	        	        int end = centerNode.getWord().length();
	        	        buffer.replace(start, end, "BIO_Entity");
	        	        candidate = buffer.toString();
	        	    }
	        	    else throw new RuntimeException("checking centerNode " + centerNode + " and protein " + protein.getProteinName()); 
	        	    /*System.out.println("original centerNode " + centerNode + " " + proteinID + " " + candidate + " " +
	        	    		sentence.getDependencyGraph(graphType).getGraph().getEdgeCount() + " edges " + 
	        	    		sentence.getDependencyGraph(graphType).getGraph().getVertexCount() + " nodes.");*/
        		    if(candidate.matches("\\S*BIO_Entity\\S+")) {
        		        Vertex v = new Vertex();
        		        String token = candidate.substring(candidate.indexOf("BIO_Entity") + 10);
        		        v.setCompareForm(token.toLowerCase());
        		        v.setTokenPosition(centerNode.getTokenPosition());
        		        v.setOffset(protein.getEndIndex());
        		        v.setToken(token);
        		        v.setWord(token);
        		        sentence.getDependencyGraph().getGraph().addVertex(v);
        		        Edge e = new Edge(centerNode, "dep", v);		    
        		        sentence.getDependencyGraph().getGraph().addEdge(e, centerNode, v); 
        		        //System.out.println("New Node " + v);
        		    }
                    if(candidate.matches("\\S+BIO_Entity\\S*")) {
                    	Vertex v = new Vertex();
        		        String token = candidate.substring(0, candidate.indexOf("BIO_Entity"));
        		        v.setCompareForm(token.toLowerCase());
        		        v.setTokenPosition(centerNode.getTokenPosition());
        		        v.setOffset(centerNode.getOffset());
        		        v.setToken(token);
        		        v.setWord(token);
        		        sentence.getDependencyGraph().getGraph().addVertex(v);
        		        Edge e = new Edge(centerNode, "dep", v);		    
        		        sentence.getDependencyGraph().getGraph().addEdge(e, centerNode, v);
        		        //System.out.println("New Node " + v);
        		    }  
                    List<Edge> inEdges = new ArrayList<Edge>();
                    for(Edge e: sentence.getDependencyGraph().getGraph().getInEdges(centerNode))
                    	inEdges.add(e);
                    List<Edge> outEdges = new ArrayList<Edge>();
                    for(Edge e: sentence.getDependencyGraph().getGraph().getOutEdges(centerNode))
                    	outEdges.add(e);
                    //finally update the current vertex info
                    centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
                    centerNode.setOffset(protein.getStartIndex());
                    centerNode.setToken(protein.getProteinName() + "-" + centerNode.getTokenPosition());
                    centerNode.setWord(protein.getProteinName());
                    //resign the edges to centerNode due to the change of the hashcode keys of centerNode above
                    for(Edge e : inEdges)
                    	sentence.getDependencyGraph().getGraph().addEdge(e, e.getGovernor(), centerNode);
                    for(Edge e : outEdges)
                    	sentence.getDependencyGraph().getGraph().addEdge(e, centerNode, e.getDependent());
                    //System.out.println("updated centerNode " + centerNode + " " + sentence.getDependencyGraph(graphType).getGraph().getEdgeCount() + " edges " + 
	        	    		//sentence.getDependencyGraph(graphType).getGraph().getVertexCount() + " nodes.");	
	        	}
	        	else
	        	    centerNode.setCompareForm("BIO_Entity NN".toLowerCase());
	        	//set Vertex fields
	        	centerNode.setIsProtein(true);
	        	centerNode.setProteinID(proteinID);
	        	//set Protein graph node field
	        	protein.setGraphNode(centerNode);
		    }	   
		}
	}
	
	/**
	 * choose the center node in order to keep only one graph node for each annotation
	 * the criteria is based on the Vertex connectivity
	 * @return
	 */
	private Vertex searchCenterNodeForAnnotationGraphNodes(Set<Vertex> graphNodes, AnnotatedSentence sentence) {
		//sort the graph nodes first from small position to big position
		List<Vertex> sorted = new ArrayList<Vertex>(graphNodes);
		Collections.sort(sorted, new MyComparator()); 
		//System.out.println("before sorting " + graphNodes); System.out.println("after sorting " + sorted);
		Vertex centerNode = null;
		boolean flag = false;
    	for(Vertex v : sorted) {
			Collection<Vertex> neighbors = sentence.getDependencyGraph().getGraph().getNeighbors(v);
			for(Vertex n : neighbors) {
				if(!graphNodes.contains(n))
					flag = true;
			}
			if(flag) { centerNode = v; break; }
		}
    	return centerNode;
	}
	
	/**
	 * search for the corresponding graph node of an annotation token
	 * @param startIndex
	 * @param endIndex
	 * @param graph
	 * @return the found graph node
	 */
	private Set<Vertex> searchGraphNodeForAnnotationToken(int startIndex, int endIndex, DirectedGraph<Vertex,Edge> graph) {
		Set<Vertex> graphNodes = new HashSet<Vertex>();
		for(Vertex node : graph.getVertices()) {
			if( (node.getOffset() >= startIndex && 
					node.getOffset() + node.getWord().length() <= endIndex) ||
				(node.getOffset() <= startIndex && 
					node.getOffset() + node.getWord().length() >= endIndex) ||
				(node.getOffset() < startIndex &&
					node.getOffset() + node.getWord().length() < endIndex &&
					node.getOffset() + node.getWord().length() > startIndex) ||
				(node.getOffset() > startIndex &&
					node.getOffset() + node.getWord().length() > endIndex &&
					node.getOffset() < endIndex)	
			) {
				graphNodes.add(node);
			}
		}
		return graphNodes;
	}
	
	/**
	 * method to process a single document and combine all the useful information
	 * including both generated information and gold annotations
	 */
	private List<AnnotatedSentence> processSingleDocument(File treeFile, File graphFileMcClosky, File offsetFile) {
		List<AnnotatedSentence> document = new ArrayList<AnnotatedSentence>();
		try {
			List<String> trees = readTreeFile(treeFile);
			//McCloksy dependency output
			List<String> graphsM = readGraphFile(graphFileMcClosky);
			List<List<Integer>> offsets = readOffsetFile(offsetFile);

			//iterate each sentence in the document
			for(int i = 0; i < trees.size(); i++) {
				//System.out.println("This is the #" + (i+1) + " sentence." );
				int endIndex;
				//compute the sentence end index
				if(i == trees.size()-1)
					endIndex = -1;
				else
					endIndex = offsets.get(i+1).get(0);
				ReadSingleSentenceOutput singleSentenceOutput = new ReadSingleSentenceOutput(i+1, endIndex, trees.get(i), offsets.get(i), graphsM.get(i));
			    document.add(singleSentenceOutput);
			}		
		}catch(IOException e) {
			e.printStackTrace();
			System.out.println(e.getMessage());
		}
		return document; 
	}
	
	/**
	 * @param treeFile
	 *            input file in the PennTree bank style tree format
	 * @return a list of trees
	 * @throws IOException 
	 */
	private static List<String> readTreeFile(File treeFile) throws IOException {
		if (!treeFile.getName().matches("^\\S+\\.(pstree)$")) {
			throw new RuntimeException("invalid syntax tree file! Should end with suffix \"pstree\" " + treeFile.getName());
		}
		List<String> pennTrees = new ArrayList<String>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(treeFile, CharacterEncoding.UTF_8, null);
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				pennTrees.add(line);
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return pennTrees;
	}
	
	/**
	 * @param offsetFile
	 *            input file in the offset format
	 * @return a list of sentence offsets
	 * @throws IOException 
	 */
	private static List<List<Integer>> readOffsetFile(File offsetFile) throws IOException {
		if (!offsetFile.getName().matches("^\\S+\\.(offset)$")) {
			throw new RuntimeException("invalid offset file! Should end with suffix \"offset\" " + offsetFile.getName());
		}
		List<List<Integer>> offsets = new ArrayList<List<Integer>>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(offsetFile, CharacterEncoding.UTF_8, null);
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				List<Integer> sentenceOffsets = new ArrayList<Integer>();
				//convert each offset string into integer
				for(String offset : split(line, " "))
					sentenceOffsets.add(Integer.parseInt(offset));
				offsets.add(sentenceOffsets);
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return offsets;
	}
	
	/**
	 * @param graphFile
	 *            input file in the dependency graph format
	 * @return a list of sentence graphs
	 * @throws IOException 
	 */
	private static List<String> readGraphFile(File graphFile) throws IOException {
		if (!graphFile.getName().matches("^\\S+\\.(dep)$")) {
			throw new RuntimeException("invalid dependency graph file! Should end with suffix \"dep\" " + graphFile.getName());
		}
		List<String> graphs = new ArrayList<String>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(graphFile, CharacterEncoding.UTF_8, null);
			List<String> representations = new ArrayList<String>();
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				if(line.trim().length() == 0) {
					graphs.add( join(representations, "\t") );
					representations.clear();
				}
				else
					representations.add(line.trim());
			}
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return graphs;
	}
	
	/**
	 * @param a1File
	 *            input file in the BioNLP '09 .a1 file format
	 * @return mapping from protein ID, e.g.T5, to the {@link Protein} itself
	 * @throws IOException
	 */
	private Map<String, Protein> readA1File(File a1File) throws IOException {
		Map<String, Protein> proteinAnnotation = new HashMap<String, Protein>();
		StreamLineIterator lineIter = null;
		try {
			lineIter = new StreamLineIterator(a1File, CharacterEncoding.UTF_8, null);
			String lastProteinID = null;
			while (lineIter.hasNext()) {
				String line = lineIter.next().getText();
				if (!line.matches("^(T\\d+)\\tProtein\\s(\\d+)\\s(\\d+)\\t(.+)$")) {
					throw new RuntimeException("The protein record: " + line + " is not valid. Please check.");
				}
				Protein protein = new Protein(line);
				proteinAnnotation.put(protein.getProteinID(), protein);
				lastProteinID = protein.getProteinID();
			}
			String pmid = a1File.getName().split("\\.")[0];
			if(lastProteinID != null)
			    lastProteinIDOfEachDocument.put(pmid, Integer.parseInt(lastProteinID.substring(1))); 
		} finally {
			if (lineIter != null) {
				lineIter.close();
			}
		}
		return proteinAnnotation;
	}

	/**
	 * s compact DIY string splitting method
	 * @param s : string to split
	 * @param separator : separator for the string to be split on
	 * @return a list of split substrings
	 */
    public static final List<String> split(final String s, final String separator) {
        int lastIndex = 0, currentIndex = 0;
        List<String> strArray= new ArrayList<String>();        
        while ((currentIndex = s.indexOf(separator, lastIndex)) != -1) {
        	strArray.add( s.substring(lastIndex, currentIndex) );               		
            lastIndex = currentIndex + separator.length();
        }
        if(s.substring(lastIndex).length() != 0)
            strArray.add( s.substring(lastIndex) );        
        return strArray;        
    }
    
    /**
	 * static method to concatenate String items with a specified delimiter
	 * @param s
	 * @param delimiter
	 * @return concatenated String items with a specified delimiter
	 */
	public static final String join(Collection<String> s, String delimiter) {
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
	
	/**
	 * retrieve fully annotated documents combined with dependency graphs
	 * @return documents
	 */
	public Map<String, List<AnnotatedSentence>> getAnnotatedDocuments() {
		return documents;
	}

	public Map<String, List<AnnotatedSentence>> getIdsToAnnotatedSentences() {        
		return documents;
    }
	
	/**
	 * retrieve last protein ID of all documents
	 * @return lastProteinIDOfEachDocument
	 */
	public Map<String, Integer> getLastProteinIDOfDocuments() {
		return lastProteinIDOfEachDocument;
	}
}

class MyComparator implements Comparator<Vertex> {
    @Override
    public int compare(Vertex o1, Vertex o2) {  
      if (o1.getTokenPosition() < o2.getTokenPosition()) {
         return 1;
      } else if (o1.getTokenPosition() > o2.getTokenPosition()) {
         return -1;
      }
      return 0;
    }
}
