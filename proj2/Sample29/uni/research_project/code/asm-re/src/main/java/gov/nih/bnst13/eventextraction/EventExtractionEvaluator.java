package gov.nih.bnst13.eventextraction;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.nicta.biomed.bnst13.utils.ResourceExtractor;

import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;

public class EventExtractionEvaluator {
	private static final Logger LOG = LoggerFactory.getLogger(EventExtractionEvaluator.class);

	private String eventPredictionPath;
	private String eventEvalPath;
	private String goldPath;
	
	public static final Runtime RUNTIME = Runtime.getRuntime();

	public EventExtractionEvaluator(String eventPredictionPath, String eventEvalPath,
			String goldPath) {
		this.eventPredictionPath = eventPredictionPath;
		this.eventEvalPath = eventEvalPath;
		this.goldPath = goldPath;
	}

	/**
	 * evaluate the predicted events using gold event annotation and print the
	 * evaluation results
	 */
	public String getAggregateEvaluation() {
		if (eventPredictionPath == null)
			throw new RuntimeException("Event prediction must be run before evaluation");
		LOG.debug("Starting to evaluate predicted events.........");
		// remove the eval folder content for cleaning

		try {
			writeEvalFiles();
			Process process = Runtime.getRuntime().exec(getScorerScript(), null,
					new File(eventEvalPath).getParentFile());
			InputStream is = process.getInputStream();
			InputStreamReader isr = new InputStreamReader(is);
			BufferedReader br = new BufferedReader(isr);
			String line;
			StringBuffer resOutput = new StringBuffer();
			while ((line = br.readLine()) != null) {
				LOG.trace("Read aggregate line {}", line);
				resOutput.append(line);
				resOutput.append("\n");
			}

                        process.waitFor();
                        process.destroy();
                        process.getOutputStream().close();
                        //process.getInputStream().close();
br.close();
                        process.getErrorStream().close();
System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();System.gc();

			return resOutput.toString();
		} catch (IOException e) {
			throw new RuntimeException(e);
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		}
	}
	
	protected String evaluateSingle(File inputFile) {
		return evaluateSingle(inputFile, goldPath);
	}
	
	public static String evaluateSingle(File inputFile, String goldPath) {
		long startTime = System.currentTimeMillis();
		String normCmdLine = getNormalizeScript() + " -g " + goldPath + " -u "
				+ inputFile.getAbsolutePath();
		try {
			LOG.debug("Normalizing using: {}", normCmdLine);
			Process normProcess = Runtime.getRuntime().exec(normCmdLine, null);
			LOG.trace("Closing streams");
			normProcess.getOutputStream().close();
			normProcess.getInputStream().close();
			normProcess.getErrorStream().close(); // so crazy it just might work
			LOG.trace("Waiting for norm process to finish");
			normProcess.waitFor();
			LOG.trace("destroying norm process");
			normProcess.destroy();
			String evalCmdLine = getEvaluateScript() + " -g " + goldPath + " -sp "
					+ inputFile.getCanonicalPath();
			LOG.debug("Evaluating using: {}", evalCmdLine);
			Process evalProcess = Runtime.getRuntime().exec(evalCmdLine, null);
			InputStream is = evalProcess.getInputStream();
			InputStreamReader isr = new InputStreamReader(is);
			BufferedReader br = new BufferedReader(isr);
			long postScriptTime = System.currentTimeMillis();
			LOG.debug("Running eval/norm perl scripts took {} ms", postScriptTime - startTime);
			StringBuffer results = new StringBuffer();
			String line = null;
			while ((line = br.readLine()) != null) {
				LOG.trace("Read eval line {}", line);
				results.append(line);
				results.append("\n");
			}
			LOG.debug("Post-script eval took {} ms", System.currentTimeMillis() - postScriptTime);
			LOG.trace("... done evaluating {}", inputFile);
			br.close();
			//isr.close();
			//is.close();
			evalProcess.getErrorStream().close(); // gah - why is this needed?
			evalProcess.getOutputStream().close();
			evalProcess.waitFor();
			evalProcess.destroy();
			return results.toString();
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

	}

	void writeEvalFiles() throws IOException, InterruptedException {
		try {
			File directory = new File(eventPredictionPath);
			if (!directory.isDirectory())
				throw new RuntimeException(directory.getAbsolutePath() + " is not a directory");
			File[] listOfFiles = directory.listFiles();
			for (File inputFile : listOfFiles) {
				if (!inputFile.isFile() || !inputFile.getName().matches("^\\S+\\.a2$"))
					continue;
				String outputFileName = inputFile.getName().split("\\.")[0] + ".eval";
				File outputFile = new File(eventEvalPath, outputFileName);
				outputFile.getParentFile().mkdirs();
				BufferedWriter output;
				try {
					output = FileWriterUtil.initBufferedWriter(outputFile, CharacterEncoding.UTF_8,
							WriteMode.OVERWRITE, FileSuffixEnforcement.OFF);
				} catch (FileNotFoundException e) {
					throw new RuntimeException("Unable to open the output file: " + outputFileName,
							e);
				}
				String singleEval = evaluateSingle(inputFile);
				LOG.trace("Got eval results for {}: {}", inputFile, singleEval);
				output.write(singleEval);
				output.close();
			}
		} catch (IOException e) {
			throw new RuntimeException(e);
		} 
	}

	static String getEvaluateScript() {
		return "perl " + getScript("helper-scripts/a2-evaluate.pl");
	}

	static String getNormalizeScript() {
		return "perl " + getScript("helper-scripts/a2-normalize.pl");
	}

	static String getScorerScript() {
		return "perl " + getScript("helper-scripts/PRF.pl");
	}

	private static String getScript(String scriptPath) {
		try {
			return ResourceExtractor.getExtractedResource(scriptPath).getCanonicalPath();
		} catch (IOException e) {
			throw new RuntimeException("Could not extract script " + scriptPath, e);
		}
	}

}
