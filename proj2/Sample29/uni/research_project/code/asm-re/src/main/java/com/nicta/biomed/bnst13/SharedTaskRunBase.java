package com.nicta.biomed.bnst13;

import gov.nih.bnst13.preprocessing.annotation.DocumentProducer;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Properties;

import org.kohsuke.args4j.CmdLineException;
import org.kohsuke.args4j.CmdLineParser;
import org.kohsuke.args4j.Option;

import com.nicta.biomed.bnst13.annotations.AnnotatedCPDocsFromDirectory;
import com.nicta.biomed.bnst13.annotations.StanfordDepDocProducer;
import com.nicta.biomed.bnst13.textprocess.GraphLabelTransformer;
import com.nicta.biomed.bnst13.textprocess.GraphTransformer;
import com.nicta.biomed.bnst13.textprocess.StanfordCCProcessedTransformer;

public class SharedTaskRunBase {
	protected enum ParseSource { CLEARPARSER, STANFORD }
	
	
	protected GraphTransformer graphTransformer = null;

	@Option(name = "-g", aliases = { "--graph-label-transforms" }, usage = "Transform the graphs labels using"
			+ "the mappings from this properties file")
	protected String graphLabelTransformsFilename = "";

	@Option(name = "-c", aliases = { "--stanford-cc-prop"}, usage = "Convert graphs to Stanford CCpropagated form")
	protected boolean ccPropForm = false;
	
	@Option(name = "-p", aliases = { "--parse-source" }, usage = "Which parser to use to create the parses")
	protected ParseSource parseSource = ParseSource.CLEARPARSER;

	protected static GraphTransformer transformerFromLabelMapFile(String filename) {
		Map<String, String> graphLabelTransforms = readStringMapFromPropertiesFile(filename);
		return new GraphLabelTransformer(graphLabelTransforms);
	}

	protected void readArgs(String[] cliArgs) {
		CmdLineParser parser = new CmdLineParser(this);
		try {
			parser.parseArgument(cliArgs);
		} catch (CmdLineException e) {
			System.err.println(e.getMessage());
			parser.printUsage(System.err);
		}
	}

	static Map<String, String> readStringMapFromPropertiesFile(String filename) {
		Properties props = readProperties(filename);
		Map<String, String> values = new HashMap<String, String>();
		for (Entry<Object, Object> p : props.entrySet())
			values.put((String) p.getKey(), (String) p.getValue());
		return values;
	}

	protected static Properties readProperties(String filename) {
		Properties props = new Properties();
		try {
			props.load(new FileInputStream(filename));
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
		return props;
	}

	public SharedTaskRunBase() {
		super();
	}

	protected void init() {
		if (!graphLabelTransformsFilename.isEmpty()) 
			graphTransformer = transformerFromLabelMapFile(graphLabelTransformsFilename);
		if (ccPropForm) {
			if (graphTransformer != null)
				throw new RuntimeException("It is not possible ot specify multiple graph transformers");
			graphTransformer = new StanfordCCProcessedTransformer();
		}
	}
	
	protected DocumentProducer getDocProducer(String parseDir, String annDataDir) {
		return getDocProducer(parseDir, annDataDir, true);
	}

	protected DocumentProducer getDocProducer(String parseDir, String annDataDir, boolean forTraining) {
		DocumentProducer docProd = null;
		if (parseSource == ParseSource.CLEARPARSER) {
			AnnotatedCPDocsFromDirectory annCpDocs = new AnnotatedCPDocsFromDirectory(parseDir, annDataDir, forTraining);
			if (graphTransformer != null)
				annCpDocs.setGraphTransformer(graphTransformer);
			docProd = annCpDocs;
		} else if (parseSource == ParseSource.STANFORD) {
			docProd = new StanfordDepDocProducer(parseDir, annDataDir);
			if (graphTransformer != null)
				throw new RuntimeException("Cannot transform Stanford dep graphs");
		}
		return docProd;
	}

}
