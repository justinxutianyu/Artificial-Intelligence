package gov.nih.bnst13.preprocessing.combine.training;

import gov.nih.bnst13.patternlearning.EventRule;
import gov.nih.bnst13.preprocessing.annotation.Event;
import gov.nih.bnst13.preprocessing.annotation.Protein;
import gov.nih.bnst13.preprocessing.annotation.Trigger;
import gov.nih.bnst13.preprocessing.dp.DependencyGraph;
import gov.nih.bnst13.preprocessing.dp.Vertex;

import java.util.List;
import java.util.Map;
import java.util.Set;

public interface AnnotatedSentence {

	/**
	 * retrieve the dependency graph
	 * @return dependency graph
	 */
	public abstract DependencyGraph getDependencyGraph();

	/**
	 * retrieve sentence ID of the sentence
	 * @return sentence ID
	 */
	public abstract int getSentenceID();

	/**
	 * retrieve start index of the sentence
	 * @return startIndex
	 */
	public abstract int getStartIndex();

	/**
	 * retrieve end index of the sentence
	 * @return endIndex
	 */
	public abstract int getEndIndex();

	/**
	 * retrieve all event rules of the sentence
	 * @return eventRulesOfSentence
	 */
	public abstract List<EventRule> getEventRulesOfSentence();

	/**
	 * set all event rules of the sentence
	 */
	public abstract void setEventRulesOfSentence(List<EventRule> eventRulesOfSentence);

	/**
	 * set proteins for the sentence
	 * @param proteins
	 */
	public abstract void setProteins(Map<String, Protein> proteins);

	/**
	 * retrieve proteins of the sentence
	 * @return proteins
	 */
	public abstract Map<String, Protein> getProteins();

	/**
	 * set triggers for the sentence
	 * @param triggers
	 */
	public abstract void setTriggers(Map<String, Trigger> triggers);

	/**
	 * retrieve triggers of the sentence
	 * @return triggers
	 */
	public abstract Map<String, Trigger> getTriggers();

	/**
	 * set events for the sentence
	 * @param triggers
	 */
	public abstract void setEvents(Map<String, Event> events);

	/**
	 * retrieve events of the sentence
	 * @return events
	 */
	public abstract Map<String, Event> getEvents();

}