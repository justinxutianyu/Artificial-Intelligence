package com.unimelb.biomed.annotations.extractor;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.unimelb.biomed.extractor.annotations.AnnotatedDocCollection;

public class AnnotatedCorpus {

    ////////////////////////
    // Instance Variables //
    ////////////////////////

    private static final Logger LOG =
        LoggerFactory.getLogger(AnnotatedCorpus.class);

    //Name of the corpus
    private String name;

    //Training, test and dev data sets
    private AnnotatedDocCollection trainingData;
    private AnnotatedDocCollection testData;
    private AnnotatedDocCollection devData;

    //Named entity annotations
    private String entityFileExtension;
    private String entityFileFormat;

    //Event annotations
    private String eventFileExtension;
    private String eventFileFormat;

    //Relation annotations
    private String relationFileExtension;
    private String relationFileFormat;

    ////////////////////////
    // Class Constructors //
    ////////////////////////

    public AnnotatedCorpus(
        String name,
        AnnotatedDocCollection trainingData,
        AnnotatedDocCollection testData,
        AnnotatedDocCollection devData
    ) {
        this.name = name;
        this.trainingData = trainingData;
        this.testData = testData;
        this.devData = devData;
    }

    //////////////////////
    // Accessor Methods //
    //////////////////////

    //Entity Annotations
    public void setEntityFileFormat(String format) {
        this.entityFileFormat = format;
    }

    public String getEntityFileFormat(String format) {
        return entityFileFormat;
    }

    public void setEntityFileExtension(String extension) {
        this.entityFileExtension = extension;
    }

    public String getEntityFileExtension(String extension) {
        return entityFileExtension;
    }

    //Event Annotations
    public void setEventFileFormat(String format) {
        this.eventFileFormat = format;
    }

    public String getEventFileFormat(String format) {
        return eventFileFormat;
    }

    public void setEventFileExtension(String extension) {
        this.eventFileExtension = extension;
    }

    public String getEventFileExtension(String extension) {
        return eventFileExtension;
    }

    //Relation Annotations
    public void setRelationFileFormat(String format) {
        this.relationFileFormat = format;
    }

    public String getRelationFileFormat(String format) {
        return relationFileFormat;
    }

    public void setRelationFileExtension(String extension) {
        this.relationFileExtension = extension;
    }

    public String getRelationFileExtension(String extension) {
        return relationFileExtension;
    }

    /////////////////
    // API Methods //
    /////////////////

    public boolean hasEntityAnnotations() {
        return !this.entityFileFormat.equals("")
            && !this.entityFileExtension.equals("");
    }

    public boolean hasEventAnnotations() {
        return !this.eventFileFormat.equals("")
            && !this.eventFileExtension.equals("");
    }

    public boolean hasRelationAnnotations() {
        return !this.relationFileFormat.equals("")
            && !this.relationFileExtension.equals("");
    }

}
