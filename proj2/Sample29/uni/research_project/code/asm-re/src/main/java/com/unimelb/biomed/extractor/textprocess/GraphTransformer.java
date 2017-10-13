package com.unimelb.biomed.extractor.textprocess;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.googlecode.clearnlp.dependency.DEPTree;

import edu.uci.ics.jung.graph.DirectedGraph;
import gov.nih.bnst.preprocessing.dp.Edge;
import gov.nih.bnst.preprocessing.dp.Vertex;

public interface GraphTransformer {
	public DirectedGraph<Vertex, Edge> transform(DirectedGraph<Vertex, Edge> orig);
}
