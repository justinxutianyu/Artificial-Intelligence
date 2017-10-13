package gov.nih.bnst.preprocessing.combine.training;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import gov.nih.bnst.preprocessing.dp.DependencyGraph;
import gov.nih.bnst.preprocessing.pt.PennTree;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;

import org.junit.Test;

/**
 * <br>
 * Unit test cases to test the implementation of the CombineInfo module</br> <br>
 * </br>
 * 
 * @author Tested by Haibin Liu </br>
 * 
 */
public class CombineInfoTest {

	private CombineInfo combine = new CombineInfo("M");

	/**
	 * Checking if the info is correctly combined for a sentence
	 */
	@Test
	public void isSentenceInfoCombinedCorrect() {
		String tree = "(S1 (S (S (NP (NN BMP-6)) (VP (VBZ inhibits) (NP (NP (NN growth)) (PP (IN of) (NP (JJ mature) (JJ human) (NN B) (NNS cells)))))) (: ;) (NP (NP (NP (NN induction)) (PP (IN of) (NP (NN Smad) (NN phosphorylation)))) (CC and) (NP (NP (NN upregulation)) (PP (IN of) (NP (NN Id1)))))))";
		String offsetString = "0 6 15 22 25 32 38 40 45 47 57 60 65 81 85 98 101";
		List<Integer> offset = new ArrayList<Integer>();
		for (String s : offsetString.split("\\s"))
			offset.add(Integer.parseInt(s));

		String[] graphs = new String[] {
				"nsubj(inhibits-2, BMP-6-1)	root(ROOT-0, inhibits-2)	dobj(inhibits-2, growth-3)	amod(cells-8, mature-5)	amod(cells-8, human-6)	nn(cells-8, B-7)	prep_of(growth-3, cells-8)	dep(inhibits-2, induction-10)	nn(phosphorylation-13, Smad-12)	prep_of(induction-10, phosphorylation-13)	dep(inhibits-2, upregulation-15)	conj_and(induction-10, upregulation-15)	prep_of(upregulation-15, Id1-17)",
				"root(ROOT-0, BMP-6-1)	dep(BMP-6-1, inhibits-2)	dobj(inhibits-2, growth-3)	amod(cells-8, mature-5)	amod(cells-8, human-6)	nn(cells-8, B-7)	prep_of(growth-3, cells-8)	dep(BMP-6-1, induction-10)	nn(phosphorylation-13, Smad-12)	prep_of(induction-10, phosphorylation-13)	prep_of(induction-10, upregulation-15)	conj_and(phosphorylation-13, upregulation-15)	prep_of(phosphorylation-13, Id1-17)" };
		for (String graph : graphs) {
			ReadSingleSentenceOutput singleSentenceOutput = new ReadSingleSentenceOutput(1, 1000,
					tree, offset, graph);
			DependencyGraph g = singleSentenceOutput.getDependencyGraph();
			PennTree t = singleSentenceOutput.getPennTree();
			// test tree token
			assertEquals(true, t.getTokens().get(9).getWord().equals("induction"));
			assertEquals(true, t.getTokens().get(9).getTokenPosition() == 10);
			assertEquals(true, t.getTokens().get(9).getPOSTag().equals("NN"));
			assertEquals(true, t.getTokens().get(9).getLemma().equals("induction"));
			assertEquals(true, t.getTokens().get(9).getOffset() == 47);
			assertEquals(true, t.getTokens().get(9).getNounPhrase().toString().equals("induction"));
			// test graph node
			assertEquals(true, g.getNodeFromToken("induction-10").getOffset() == 47);
			assertEquals(true, g.getNodeFromToken("induction-10").getLemma().equals("induction"));
			assertEquals(true, g.getNodeFromToken("induction-10").getOffset() == g.getNodeFromToken(
					"induction-10").getTreeToken().getOffset());
		}
	}

	@Test
	public void isFileCorrectlyRead() {
		combine.processSharedTaskDirectory();
	}
}
