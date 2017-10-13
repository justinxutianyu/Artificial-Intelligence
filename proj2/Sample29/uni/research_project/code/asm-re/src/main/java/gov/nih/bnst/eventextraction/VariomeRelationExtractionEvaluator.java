package gov.nih.bnst.eventextraction;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.utils.ResourceExtractor;

import edu.ucdenver.ccp.common.file.CharacterEncoding;
import edu.ucdenver.ccp.common.file.FileUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil;
import edu.ucdenver.ccp.common.file.FileWriterUtil.FileSuffixEnforcement;
import edu.ucdenver.ccp.common.file.FileWriterUtil.WriteMode;

public class VariomeRelationExtractionEvaluator {
	private static final Logger LOG =
        LoggerFactory.getLogger(VariomeRelationExtractionEvaluator.class);

	private String relationPredictionPath;
	private String relationEvalPath;
	private String goldPath;
    private String rulePath;

	public static final Runtime RUNTIME = Runtime.getRuntime();

	public VariomeRelationExtractionEvaluator(
        String relationPredictionPath,
        String relationEvalPath,
		String goldPath,
        String rulePath
    ) {
		this.relationPredictionPath = relationPredictionPath;
		this.relationEvalPath = relationEvalPath;
		this.goldPath = goldPath;
        this.rulePath = rulePath;
	}

	/**
	 * evaluate the predicted events using gold event annotation and print the
	 * evaluation results
	 */
	public String getAggregateEvaluation() {
		if (relationPredictionPath == null) {
			throw new RuntimeException(
                "Event prediction must be run before evaluation"
            );
        }

        LOG.debug("Starting to evaluate predicted events.........");

        // Remove the eval folder content for cleaning
		try {
			writeEvalFiles();

            //Execute the scoring script
            String scorerScript = getScorerScript() +
                " -r " + (new File(rulePath)).getCanonicalPath();
            LOG.info("Running scorer script: {}", scorerScript);
            Process process = Runtime
                .getRuntime()
                .exec(
                    scorerScript,
                    null,
				    new File(relationEvalPath).getParentFile()
                );
            InputStream is = process.getInputStream();
			InputStreamReader isr = new InputStreamReader(is);
			BufferedReader br = new BufferedReader(isr);
			String line;
			StringBuffer resOutput = new StringBuffer();

            while ((line = br.readLine()) != null) {
				LOG.debug("Read aggregate line {}", line);
				resOutput.append(line);
				resOutput.append("\n");
			}

            process.waitFor();
            br.close();
            isr.close();
            is.close();
            process.destroy();

            return resOutput.toString();
        } catch (IOException e) {
			throw new RuntimeException(e);
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		}
	}

	protected String evaluateSingle(File inputFile) {
		return evaluateSingle(inputFile, goldPath, rulePath);
	}

	public static String evaluateSingle(
        File inputFile,
        String goldPath,
        String rulePath
    ) {
		long startTime = System.currentTimeMillis();

        try {
            //Run evaluation script
			String evalCmdLine =
                getEvaluateScript()
                + " -g " + goldPath
                + " -r " + (new File(rulePath)).getCanonicalPath()
                + " " + inputFile.getCanonicalPath();
			LOG.debug("Evaluating using: {}", evalCmdLine);
            Process evalProcess = Runtime
                .getRuntime()
                .exec(evalCmdLine, null);
			InputStream is = evalProcess.getInputStream();
			InputStreamReader isr = new InputStreamReader(is);
			BufferedReader br = new BufferedReader(isr);
			long postScriptTime = System.currentTimeMillis();

            LOG.debug(
                "Running eval perl scripts took {} ms",
                postScriptTime - startTime
            );

            //Retrieve results from buffered reader
            StringBuffer results = new StringBuffer();
			String line = null;
			while ((line = br.readLine()) != null) {
				LOG.info("Read eval line {}", line);
				results.append(line);
				results.append("\n");
			}
			LOG.debug(
                "Post-script eval took {} ms",
                System.currentTimeMillis() - postScriptTime
            );
			LOG.info("... done evaluating {}", inputFile);

            br.close();
            evalProcess.waitFor();
            evalProcess.getErrorStream().close(); // gah - why is this needed?
			evalProcess.getOutputStream().close();
			evalProcess.destroy();

            return results.toString();
		} catch (InterruptedException e) {
			throw new RuntimeException(e);
		} catch (IOException e) {
			throw new RuntimeException(e);
		}

	}

	private void writeEvalFiles() throws IOException, InterruptedException {
		try {
            //Check the directory containing predictions is valid
            File directory = new File(relationPredictionPath);
			if (!directory.isDirectory())
				throw new RuntimeException(
                    directory.getAbsolutePath() + " is not a directory"
                );

            //Loop over prediction files
            File[] listOfFiles = directory.listFiles();
			for (File inputFile : listOfFiles) {
                //Check that predicted ANN file is valid
                if (!inputFile.isFile() || !inputFile.getName().matches("^\\S+\\.ann$"))
					continue;

                //Initialize output evaluation file
                String outputFileName =
                    inputFile
                        .getName()
                        .split("\\.")[0] + ".eval";
				File outputFile
                    = new File(relationEvalPath, outputFileName);
				outputFile.getParentFile().mkdirs();

                BufferedWriter output;
				try {
					output = FileWriterUtil.initBufferedWriter(
                        outputFile,
                        CharacterEncoding.UTF_8,
						WriteMode.OVERWRITE,
                        FileSuffixEnforcement.OFF
                    );
				} catch (FileNotFoundException e) {
					throw new RuntimeException(
                        "Unable to open the output file: "
                        + outputFileName, e);
				}

                //Evaluate the prediction file
				String singleEval = evaluateSingle(inputFile);
				LOG.trace(
                    "Got eval results for {}: {}",
                    inputFile,
                    singleEval
                );

                //Write the results to an output file
                output.write(singleEval);
				output.close();
			}
		} catch (IOException e) {
			throw new RuntimeException(e);
		}
	}

	static String getEvaluateScript() {
		return "perl " + getScript("helper-scripts/ann-evaluate.pl");
	}

	//static String getNormalizeScript() {
	//	return "perl " + getScript("helper-scripts/ann-normalize.pl");
	//}

	static String getScorerScript() {
		return "perl " + getScript("helper-scripts/PRF_variome.pl");
	}

	private static String getScript(String scriptPath) {
		try {
			return ResourceExtractor
                .getExtractedResource(scriptPath)
                .getCanonicalPath();
		} catch (IOException e) {
			throw new RuntimeException(
                "Could not extract script "
                 + scriptPath, e
            );
		}
	}

}
