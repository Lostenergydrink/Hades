import { AssertionGraph, AtomicClaim, RelationshipType } from '../core/types';

export class MoiraeWeaver {
  
  public weave(graph: AssertionGraph, survivedIds: Set<string>): string {
    const threads = graph.nodes.filter(n => survivedIds.has(n.id));
    
    try {
      const sorted = this.topologicalSort(threads, graph.edges);
      // Weave logic: Just concatenation for now, but following dependency order
      return sorted.map(t => t.payload.fragment).join('\n\n');
    } catch (e) {
      throw new Error(`MOIRAE_COLLAPSE: ${e instanceof Error ? e.message : 'Unknown error'}`);
    }
  }

  private topologicalSort(
      nodes: AtomicClaim[], 
      edges: { from: string; to: string; type: RelationshipType }[]
  ): AtomicClaim[] {
    
    const sorted: AtomicClaim[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const visit = (node: AtomicClaim) => {
      if (visiting.has(node.id)) {
        throw new Error(`Cycle detected at node ${node.id} (${node.subject})`);
      }
      if (visited.has(node.id)) return;

      visiting.add(node.id);

      // Find dependencies: Nodes that SUPPORT this node
      // Edge: From (Support) -> To (Dependent)
      const deps = edges
        .filter(e => e.to === node.id && e.type === 'SUPPORTS')
        .map(e => nodes.find(n => n.id === e.from))
        .filter((n): n is AtomicClaim => !!n);

      deps.forEach(visit);

      visiting.delete(node.id);
      visited.add(node.id);
      sorted.push(node);
    };

    nodes.forEach(visit);
    return sorted;
  }
}
