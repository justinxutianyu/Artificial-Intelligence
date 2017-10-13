package com.unimelb.biomed.extractor;

import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.annotations.BnstRuntimeException;

public class SharedTaskHelper {
	private static final Logger LOG = LoggerFactory.getLogger(SharedTaskHelper.class);
	public static final String ENTITIES_FILE_SUFFIX = ".a1";
	public static final String EVENTS_FILE_SUFFIX = ".a2";
	public static final String PARSEABLE_SUFFIX = ".txt";
	public static final String PARSED_SUFFIX = ".txt.parsed";
	public static final String LEARNED_RAW_RULES_DIR = "training/inferred-rules";
	public static final String OPTIMIZED_RULES_DIR = "training/optimized-rules";
	public static final String TRAINING_PARSE_DIR = "training/parse";

	/** if we have multiple parse dirs, they must match this pattern: */
	public static final Pattern PARSE_VARIANT_NAME_PTN = Pattern.compile("^parse\\.variant-\\d+$");
	public static final String TEST_PARSE_DIR = "test/parse";
	public static final String TEST_EVAL_DIR = "test/eval";
	public static final String TEST_PREDICTIONS_DIR = "test/predictions";
	public static final String TEST_RESULTS_FILE = "test/RESULTS";
	public static final String TUNING_PARSE_DIR = "tuning/parse";
	public static final String TUNING_PREDICTIONS_DIR = "tuning/predictions";
	public static final String TUNING_EVAL_DIR = "tuning/eval";


	protected static final Pattern PARSEABLE_SUFFIX_PATTERN = Pattern.compile(Pattern
			.quote(PARSEABLE_SUFFIX) + "$");
	protected static final Pattern PARSED_SUFFIX_PATTERN = Pattern.compile(Pattern
			.quote(PARSED_SUFFIX) + "$");

	private static String auxFileForParsedFile(String inputFile, String suffix) {
		Matcher matcher = PARSED_SUFFIX_PATTERN.matcher(inputFile);
		if (!matcher.find())
			LOG.error("Filename {} does not match expected suffix regex {}", inputFile,
					PARSED_SUFFIX_PATTERN);
		return matcher.replaceFirst(suffix);
	}

	private static String auxFileForParsedFile(String inputFile, String suffix, String taskDataDir) {
		File plain = new File(auxFileForParsedFile(inputFile, suffix));
		if (taskDataDir == null)
			return plain.getPath();
		else
			return new File(taskDataDir, plain.getName()).getPath();
	}

    public static String entityFileForTextFile(String inputFile) {
		return auxFileForTextFile(inputFile, ENTITIES_FILE_SUFFIX);
	}

    public static String entityFileForTextFile(String inputFile, String fileExtension) {
		return auxFileForTextFile(inputFile, fileExtension);
	}

	public static String eventFileForTextFile(String inputFile) {
		return auxFileForTextFile(inputFile, EVENTS_FILE_SUFFIX);
	}

	private static String auxFileForTextFile(String inputFile, String suffix) {
		Matcher matcher = PARSEABLE_SUFFIX_PATTERN.matcher(inputFile);
		if (!matcher.find())
			LOG.error("Filename {} does not match expected suffix regex {}", inputFile,
					PARSEABLE_SUFFIX_PATTERN);
		return matcher.replaceFirst(suffix);
	}

	public static String entityFileForParsedFile(String parsedFile) {
		return auxFileForParsedFile(parsedFile, ENTITIES_FILE_SUFFIX);
	}

	public static String eventFileForParsedFile(String parsedFile) {
		return auxFileForParsedFile(parsedFile, EVENTS_FILE_SUFFIX);
	}

	public static String entityFileForParsedFile(String parsedFile, String taskDataDir) {
		LOG.debug("returning aux file name {} for {} and task data dir {}",
				auxFileForParsedFile(parsedFile, ENTITIES_FILE_SUFFIX, taskDataDir), parsedFile, taskDataDir);
		return auxFileForParsedFile(parsedFile, ENTITIES_FILE_SUFFIX, taskDataDir);
	}

	public static String eventFileForParsedFile(String parsedFile, String taskDataDir) {
		return auxFileForParsedFile(parsedFile, EVENTS_FILE_SUFFIX, taskDataDir);
	}

    public static String entityFileForParsedFile(String parsedFile, String taskDataDir, String suffix) {
		return auxFileForParsedFile(parsedFile, suffix, taskDataDir);
	}

	public static String eventFileForParsedFile(String parsedFile, String taskDataDir, String suffix) {
		return auxFileForParsedFile(parsedFile, suffix, taskDataDir);
	}

	public static String docIdFromParsedFile(String parsedFile) {
		return auxFileForParsedFile(parsedFile, "");
	}

	public static String[] getParsedFiles(String parseDir) {
		File parseDirFile = new File(parseDir);
		String[] parseFiles = parseDirFile.list();
		if (parseFiles == null) {
			String canonical;
			try {
				canonical = parseDirFile.getCanonicalPath();
			} catch (IOException e) {
				canonical = parseDir + " (unknown canonical path)";
			}
			throw new BnstRuntimeException(canonical + " is not a directory");
		}
		return parseFiles;
	}


}
