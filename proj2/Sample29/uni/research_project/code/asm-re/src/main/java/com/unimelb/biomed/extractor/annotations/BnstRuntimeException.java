package com.unimelb.biomed.extractor.annotations;

public class BnstRuntimeException extends RuntimeException {
	private static final long serialVersionUID = 1L;

	public BnstRuntimeException(Throwable e) {
		super(e);
	}

	public BnstRuntimeException(String e) {
		super(e);
	}
}
