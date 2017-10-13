package com.unimelb.biomed.extractor.textprocess;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.googlecode.clearnlp.engine.EngineGetter;
import com.googlecode.clearnlp.feature.xml.POSFtrXml;
import com.googlecode.clearnlp.pos.POSTagger;
import com.googlecode.clearnlp.reader.AbstractReader;
import com.googlecode.clearnlp.tokenization.AbstractTokenizer;
import com.googlecode.clearnlp.tokenization.EnglishTokenizer;
import com.googlecode.clearnlp.util.pair.Pair;

public class BnstEngineGetter extends EngineGetter {
	private static final Logger LOG = LoggerFactory.getLogger(BnstEngineGetter.class);
	
	static public Pair<POSTagger[],Double> getPOSTaggers(InputStream stream) throws Exception
	{
		LOG.debug("Getting POS taggers from BnstEngineGetter");
		ZipInputStream zin = new ZipInputStream(stream);
		POSTagger[] taggers = null;
		double threshold = -1;
		POSFtrXml xml = null;
		BufferedReader fin;
		ZipEntry zEntry;
		String entry;
		int modId;
		
		boolean entriesRead = false;
		while ((zEntry = zin.getNextEntry()) != null)
		{
			entriesRead = true;
			entry = zEntry.getName();
			LOG.debug("Reading POS tagger entry: '{}' ", entry);
			fin   = new BufferedReader(new InputStreamReader(zin));
			
			if (entry.equals(ENTRY_CONFIGURATION))
			{
				taggers   = new POSTagger[Integer.parseInt(fin.readLine())];
				threshold = Double.parseDouble(fin.readLine());
			}
			else if (entry.equals(ENTRY_FEATURE))
			{
				xml = new POSFtrXml(getFeatureTemplates(fin));
			}
			else if (entry.startsWith(ENTRY_MODEL))
			{
				modId = Integer.parseInt(entry.substring(ENTRY_MODEL.length()));
				taggers[modId] = new BnstPosTagger(xml, fin);
			}
			else
			{
				LOG.warn("Invalid POS tagger entry: '{}'", entry);
			}
		}
		if (!entriesRead)
			LOG.error("No entries found in POS tagger model file");
		
		zin.close();
		if (taggers == null)
			throw new IllegalArgumentException("Could not read valid POS-taggers from provided tagger model file");
		return new Pair<POSTagger[],Double>(taggers, threshold);
	}

	static public Pair<POSTagger[],Double> getPOSTaggers(String modelFile) throws Exception
	{
		return getPOSTaggers(new FileInputStream(modelFile));
	}

	public static OffsettableTokenizer getTokenizerForPretokNEs(String dictFile) {
		try {
			return getTokenizerForPretokNEs(new FileInputStream(dictFile));
		} catch (FileNotFoundException e) {
			throw new RuntimeException(e);
		}
	}

	public static OffsettableTokenizer getTokenizerForPretokNEs(InputStream stream) {
		return new BnstEnglishTokenizer(new ZipInputStream(stream));
	}

}
