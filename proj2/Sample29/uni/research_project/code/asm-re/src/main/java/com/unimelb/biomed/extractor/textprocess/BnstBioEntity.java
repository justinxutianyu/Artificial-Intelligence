package com.unimelb.biomed.extractor.textprocess;

import com.googlecode.clearnlp.util.Span;

public class BnstBioEntity {

    private Span span;
    private String entityID;
    private String entityDescription;
    private String entityAnnotation;

    ////////////////////////
    // Class Constructors //
    ////////////////////////

    public BnstBioEntity(
        Span span,
        String entityID,
        String entityDescription,
        String entityAnnotation
    ) {
        this.span = span;
        this.entityID = entityID;
        this.entityDescription = entityDescription;
        this.entityAnnotation = entityAnnotation;
    }

    /////////////////////////
    // Setters and Getters //
    /////////////////////////

    public void setSpan(Span span) {
        this.span = span;
    }

    public Span getSpan() {
        return span;
    }

    public void setEntityID(String entityID) {
        this.entityID = entityID;
    }

    public String getEntityID() {
        return entityID;
    }

    public void setEntityDescription(String entityDescription) {
        this.entityDescription = entityDescription;
    }

    public String getEntityDescription() {
        return entityDescription;
    }

    public void setEntityAnnotation(String entityAnnotation) {
        this.entityAnnotation = entityAnnotation;
    }

    public String getEntityAnnotation() {
        return entityAnnotation;
    }

    ////////////////
    // Public API //
    ////////////////

    public String toString() {
        return entityAnnotation;
    }
}
