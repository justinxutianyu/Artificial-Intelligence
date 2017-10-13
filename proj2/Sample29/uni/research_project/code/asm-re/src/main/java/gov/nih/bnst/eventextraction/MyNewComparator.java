package gov.nih.bnst.eventextraction;

import java.util.Comparator;

import gov.nih.bnst.preprocessing.dp.Vertex;

public class MyNewComparator implements Comparator<Vertex> {
    @Override
    public int compare(Vertex o1, Vertex o2) {
      if (o1.getTokenPosition() > o2.getTokenPosition()) {
         return 1;
      } else if (o1.getTokenPosition() < o2.getTokenPosition()) {
         return -1;
      }
      return 0;
    }
}
