package com.nicta.biomed.bnst13;

import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RangeIndexer<K, V> {
	private static final Logger LOG = LoggerFactory.getLogger(RangeIndexer.class);

	private SortedMap<K, List<V>> indexes = new TreeMap<K, List<V>>();
	
	public void put(K key, V value) {
		if (!indexes.containsKey(key))
			indexes.put(key, new ArrayList<V>());
		LOG.trace("Adding value {} to key {}", value, key);
		indexes.get(key).add(value);
	}
	
	public List<V> inRange(K start, K end) {
		/** Return values which overlap with the supplied half-open range
		 * 
		 * I.e. where `start <= k < end`
		 */
		List<V> values = new ArrayList<V>();
		for (List<V> keyVals : indexes.subMap(start, end).values()) {
			values.addAll(keyVals);
		}
		LOG.trace("Found values {} for range {}:{}", values, start, end);
		return values;
	}
	
}
