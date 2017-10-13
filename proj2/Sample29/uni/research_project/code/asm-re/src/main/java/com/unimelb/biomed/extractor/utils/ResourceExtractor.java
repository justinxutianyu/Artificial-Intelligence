package com.unimelb.biomed.extractor.utils;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.SharedTaskHelper;

public class ResourceExtractor {
	private static final Logger LOG = LoggerFactory.getLogger(ResourceExtractor.class);

	/** Extract a resource from the classpath (jar or filesystem)
	 * to the filesystem
	 * @param relResPath -- the relative path (no leading '/') within the classpath
	 * @return the path where the resource was extracted to
	 * @throws IOException
	 */
	public static File getExtractedResource(String relResPath) throws IOException {
		String resPath = relResPath;
		File extracted = new File(relResPath);
		if (!extracted.exists() || extracted.length() == 0)
			extractResource(resPath, relResPath);
		return extracted;
	}

	public static void extractResource(String resPath, String extractPath) throws IOException {
		LOG.debug("Extracting resource at {} to {}", resPath, extractPath);
		LOG.debug("Resource URL is {}", SharedTaskHelper.class.getClassLoader().getResource(resPath));
		InputStream in = null;
		OutputStream out = null;
		File extracted = new File(extractPath);
		extracted.getParentFile().mkdirs();
		try {
			in = SharedTaskHelper.class.getClassLoader().getResourceAsStream(resPath);
			in = new BufferedInputStream(in);
			out = new FileOutputStream(extracted);
			out = new BufferedOutputStream(out);
			final int BUF = 1 << 10;
			byte[] buffer = new byte[BUF];
			int bytesRead = -1;
			while ((bytesRead = in.read(buffer)) > -1) 
				out.write(buffer, 0, bytesRead);
		} finally {
			if (in != null) in.close();
			if (out != null) out.close();
		}
	}

}
