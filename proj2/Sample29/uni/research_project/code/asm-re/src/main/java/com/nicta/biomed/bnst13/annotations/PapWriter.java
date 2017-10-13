package com.nicta.biomed.bnst13.annotations;

import gov.nih.bnst13.preprocessing.combine.training.AnnotatedSentence;

import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.util.List;

import com.googlecode.clearnlp.dependency.DEPTree;
import com.googlecode.clearnlp.util.UTOutput;
import com.nicta.biomed.bnst13.SharedTaskHelper;

public class PapWriter {
	public static final String PAP_SUFFIX = ".pap";

	void write(String parseDir) {
		File parseDirFile = new File(parseDir);
		for (String outputFile : parseDirFile.list()) {
			if (!outputFile.endsWith(SharedTaskHelper.PARSED_SUFFIX))
				continue;
			PrintStream foutPap = UTOutput.createPrintBufferedFileStream(outputFile + PAP_SUFFIX);
			try {
				AnnotatedCPDoc annDoc = new AnnotatedCPDoc(outputFile, null);
				for (AnnotatedClearparse annCp : annDoc.getAnnotatedClearParses()) {
					foutPap.println(annCp.getPAP());
				}
			} catch (IOException e) {
				throw new BnstRuntimeException(e);
			}
		}

	}

}
