import { AssertionGraph, PressureReport } from '../core/types';

// Predicates where (S, P, O1) and (S, P, O2) is a contradiction.
const EXCLUSIVE_PREDICATES = new Set([
    'returns_type',
    'has_arity',
    'defines_function' // You can't define the same function name twice with different bodies (usually)
]);

export class ErisPressureCalculator {
  
  public calculatePressure(graph: AssertionGraph): PressureReport {
    const conflictMap: Record<string, string[]> = {};
    let totalPressure = 0;
    const reasonCodes: string[] = [];

    const contradictions = this.findContradictions(graph);
    
    if (contradictions.length > 0) {
      totalPressure += 0.5;
      reasonCodes.push('ONTOLOGICAL_FRICTION');
      contradictions.forEach(c => {
        if (!conflictMap[c.from]) conflictMap[c.from] = [];
        conflictMap[c.from]!.push(c.to);
      });
    }

    // Heuristic: Circular deps or cross-source conflicts add pressure
    const sources = new Set(graph.nodes.map(n => n.sourceId));
    if (sources.size > 1 && contradictions.length > 0) {
      totalPressure += 0.2; 
    }

    return {
      totalPressure: Math.min(totalPressure, 1.0),
      conflictMap,
      isTerminal: totalPressure > 0.8,
      reasonCodes
    };
  }

  private findContradictions(graph: AssertionGraph) {
    const conflicts: { from: string, to: string }[] = [];
    const nodes = graph.nodes;

    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const A = nodes[i]!;
        const B = nodes[j]!;

        // 1. Subject match
        if (A.subject !== B.subject) continue;
        
        // 2. Predicate match AND Predicate is Exclusive
        if (A.predicate === B.predicate && EXCLUSIVE_PREDICATES.has(A.predicate)) {
            // 3. Object mismatch => Contradiction
            if (A.object !== B.object) {
                conflicts.push({ from: A.id, to: B.id });
            }
        }
      }
    }
    return conflicts;
  }
}
