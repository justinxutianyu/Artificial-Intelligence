package gov.nih.bnst.sharedtask.bioc;


import java.util.ArrayList;

/**
   Stand off annotation. The connection to the original text can be
   made through the {@code offset}, {@code length}, and possibly the
   {@code text} fields.
 */
public class Annotation {

    /**
       Id used to identify this annotation in a {@link Relation}.
    */
    public String id;

    /*
      Type of annotation.

      Options include "token", "noun phrase", "gene", and
      "disease". The valid values should be described in the {@code
      key} file.
    */
    public String type;

    /**
       A {@code Document} offset to where the annotated text begins in
       the {@code Sentence} or {@code Passage}. The value is the sum
       of the container offset and the local offset.
    */
    public int offset;

    /**
       The length of the annotationed text. While unlikely, this could
       be zero to describe an annotation that belongs between two
       characters.
    */
    public int length;

    /**
       Unless something else is defined this should be the
       annotated text. The length is redundant in this case. Other
       uses for this field would be the ontology id for the specific
       disease when the type was "disease."
    */
    public String text;

    public Annotation() {
        id = "";
        type = "";
        offset = 0;
        length = 0;
        text = "";
    }

    public void write() {
        System.out.println("id: " + id);
        System.out.println("type: " + type);
        System.out.println("offset: " + offset);
        System.out.println("length: " + length);
        System.out.println("text: " + text);
    }
}
