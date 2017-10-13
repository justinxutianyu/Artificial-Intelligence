package com.tantaman.commons.concurrent;

/*
 * Copyright 2011 Matt Crinklaw-Vogt
 * 
 * Adapted from https://github.com/tantaman/commons/tree/master/src/main/java/com/tantaman/commons/concurrent
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

import java.util.Collection;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Parallelizer {
	private static final Logger LOG = LoggerFactory.getLogger(Parallelizer.class);

	protected final ExecutorService forPool;

	public Parallelizer(int numThreads) {
		forPool = Executors.newFixedThreadPool(numThreads, new NamedThreadFactory(
				"Parallelizer.For"));
	}

	public Parallelizer() {
		this(Runtime.getRuntime().availableProcessors());
	}

	public <T> void forEach(final Iterable<T> elements, final Operation<T> operation) {
		try {
			forPool.invokeAll(createCallables(elements, operation));
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		// Lazy init; doesn't seem to work for some reason.
		/*
		for (final T element : elements) {
			forPool.submit(new Callable<Void>() {
				@Override
				public Void call() {
					try {
						operation.perform(element);
					} catch (Exception e) {
						LOG.error("Exception during execution of parallel task: {}", e);
						e.printStackTrace();
					}
					return null;
				}
			});
		}
		*/
		
	}

	public static <T> Collection<Callable<Void>> createCallables(final Iterable<T> elements,
			final Operation<T> operation) {
		List<Callable<Void>> callables = new LinkedList<Callable<Void>>();
		for (final T elem : elements) {
			callables.add(new Callable<Void>() {

				@Override
				public Void call() {
					operation.perform(elem);
					return null;
				}
			});
		}

		return callables;
	}

	public static interface Operation<T> {
		public void perform(T pParameter);
	}
}