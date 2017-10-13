package com.unimelb.biomed.extractor.annotations;

import gov.nih.bnst.preprocessing.dp.Vertex;

import java.util.ArrayList;
import java.util.List;
import java.util.SortedMap;
import java.util.TreeMap;

import com.unimelb.biomed.extractor.standeps.SDNode;


public class DepLinkedEvent {
	private String eventType;
	private List<Vertex> nodeTriggers = new ArrayList<Vertex>();
	private SortedMap<String, Arg> args = new TreeMap<String, Arg>();

	public DepLinkedEvent() {
	}

	public String getEventType() {
		return eventType;
	}

	public void setEventType(String eventType) {
		this.eventType = eventType;
	}

	public List<Vertex> getTriggers() {
		return nodeTriggers;
	}

	public void addTrigger(Vertex trigger) {
		this.nodeTriggers.add(trigger);
	}

	public SortedMap<String, Arg> getArgs() {
		return args;
	}

	public void addArg(String argName, Vertex argNode) {
		args.put(argName, new Arg(argNode));
	}

	public void addArg(String argName, DepLinkedEvent evt) {
		args.put(argName, new Arg(evt));
	}
	
	public String toString() {
		return eventType + "; TRIGGERS=" + nodeTriggers + "; ARGS=" + args;
	}

	public static class Arg {
		private Vertex node = null;
		private DepLinkedEvent evt = null;

		public Arg(Vertex node) {
			this.node = node;
		}

		public Arg(DepLinkedEvent evt) {
			this.evt = evt;
		}

		public Vertex getNode() {
			return node;
		}

		public DepLinkedEvent getEvent() {
			return evt;
		}

		public String toString() {
			if (node != null) {
				return node.toString();
			} else {
				String repres = evt.getEventType() + ":";
				boolean isFirst = true;
				for (Vertex trigger : evt.getTriggers()) {
					repres += (isFirst ? " " : "") + trigger.toString();
					isFirst = false;
				}
				return repres;
			}
		}
	}

}