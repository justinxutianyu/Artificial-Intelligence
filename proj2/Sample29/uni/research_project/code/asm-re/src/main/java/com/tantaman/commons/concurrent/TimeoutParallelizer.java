package com.tantaman.commons.concurrent;

import java.util.concurrent.TimeUnit;


public class TimeoutParallelizer extends Parallelizer {
	private int timeoutSeconds;

	public TimeoutParallelizer(int numThreads, int timeoutSeconds) {
		super(numThreads);
		this.timeoutSeconds = timeoutSeconds;
	}
	
	public <T> void forEach(final Iterable<T> elements, final Operation<T> operation) {
		try {
			forPool.invokeAll(createCallables(elements, operation), timeoutSeconds, TimeUnit.SECONDS);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
}
