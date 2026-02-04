import { createHash } from 'node:crypto';
import { AssertionGraph } from '../core/types';

export class StyxStore {
  private deadPaths: Set<string> = new Set();

  public swearOath(graph: AssertionGraph): void {
    const signature = this.sig(graph);
    this.deadPaths.add(signature);
  }

  public isBound(graph: AssertionGraph): boolean {
    return this.deadPaths.has(this.sig(graph));
  }

  private sig(graph: AssertionGraph): string {
    // V3: Canonical Signature based on content, not just unstable IDs
    // Sort nodes by Subject+Predicate+Object to ensure deterministic ordering
    const canonicalContent = graph.nodes
        .map(n => `${n.sourceId}|${n.subject}|${n.predicate}|${n.object}`)
        .sort()
        .join('||');
        
    return createHash('sha256').update(canonicalContent).digest('hex');
  }
}
