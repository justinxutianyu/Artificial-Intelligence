/*
 Copyright (c) 2012, Regents of the University of Colorado
 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification, 
 are permitted provided that the following conditions are met:

 * Redistributions of source code must retain the above copyright notice, this 
    list of conditions and the following disclaimer.
   
 * Redistributions in binary form must reproduce the above copyright notice, 
    this list of conditions and the following disclaimer in the documentation 
    and/or other materials provided with the distribution.
   
 * Neither the name of the University of Colorado nor the names of its 
    contributors may be used to endorse or promote products derived from this 
    software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
 DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
 ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

package gov.nih.bnst.preprocessing.dp;

/**
 * <p>Definition of Edge for dependency graphs</p>
 * 
 * <p>Edge is then fed into graphs of the JUNG library</p>
 * 
 * <p>The Edge definition can be modified based on one's own needs</p>
 * 
 * @author Implemented by Haibin Liu and Tested by Philippe Thomas
 *
 */
public class Edge extends edu.ucdenver.ccp.esm.Edge<Vertex> {
	public Edge(Vertex gov, String label, Vertex dep) {
		super(gov, label, dep);
	}
    
    @Override
	public int hashCode() {
		final int prime = 31;
		int result = 1;
		Vertex dep = getDependent();
		Vertex gov = getGovernor();
		String label = getLabel();
		result = prime * result + ((dep == null) ? 0 : dep.hashCode());
		result = prime * result + ((gov == null) ? 0 : gov.hashCode());
		result = prime * result + ((label == null) ? 0 : label.hashCode());
		return result;
	}

	@Override
	public boolean equals(Object obj) {
		Vertex dep = getDependent();
		Vertex gov = getGovernor();
		String label = getLabel();
		if (this == obj)
			return true;
		if (obj == null)
			return false;
		if (getClass() != obj.getClass())
			return false;
		Edge other = (Edge) obj;
		if (dep == null) {
			if (other.getDependent() != null)
				return false;
		} else if (!dep.equals(other.getDependent()))
			return false;
		if (gov == null) {
			if (other.getGovernor() != null)
				return false;
		} else if (!gov.equals(other.getGovernor()))
			return false;
		if (label == null) {
			if (other.getLabel() != null)
				return false;
		} else if (!label.equals(other.getLabel()))
			return false;
		return true;
	}

	/**
     * print edge content
     */
    @Override
	public String toString(){
    	StringBuilder sb = new StringBuilder();
    	sb.append(getLabel());
		sb.append("(");
		sb.append(getGovernor().toString());
		sb.append(", ");
		sb.append(getDependent().toString());
		sb.append(")");
		
		return sb.toString();
    }
}
