import { createHash } from 'node:crypto';
import * as ts from 'typescript';
import { z } from 'zod';
import { AtomicClaim, AssertionGraph, RelationshipType } from '../core/types';

const RawClaimSchema = z.object({
  subject: z.string(),
  predicate: z.string(),
  object: z.string(),
  provenance: z.string(),
  fragment: z.string().optional(),
  dependencies: z.array(z.string()).optional()
});

type RawClaim = z.infer<typeof RawClaimSchema>;

export class HecateDecomposer {
  
  public decompose(sourceId: string, content: string): AssertionGraph {
    const isCode = /function|const|class|import/.test(content);
    
    // Fail loudly if protocol not supported
    if (!isCode) {
      console.warn("PROTOCOL_WARNING: Non-code input detected. Protocol extraction is stubbed.");
      return { nodes: [], edges: [] };
    }

    const rawClaims = this.extractViaAST(content);

    const nodes = rawClaims
      .map(c => this.transformToAtomic(c, sourceId))
      .filter(n => n.score > 0); 

    return { 
      nodes, 
      edges: this.deriveEdges(nodes) 
    };
  }

  private extractViaAST(code: string): RawClaim[] {
    const claims: RawClaim[] = [];
    const sourceFile = ts.createSourceFile('temp.ts', code, ts.ScriptTarget.Latest, true);

    const findParentScope = (node: ts.Node): string => {
      let current = node.parent;
      while (current) {
        if (ts.isFunctionDeclaration(current) && current.name) return current.name.text;
        if (ts.isClassDeclaration(current) && current.name) return current.name.text;
        if (ts.isMethodDeclaration(current) && current.name && ts.isIdentifier(current.name)) return current.name.text;
        current = current.parent;
      }
      return 'global_scope';
    };

    const visit = (node: ts.Node) => {
      // 1. Definition Claims
      if (ts.isFunctionDeclaration(node) && node.name) {
        claims.push({
          subject: node.name.text,
          predicate: 'defines_function',
          object: 'logic_block',
          provenance: node.getText(sourceFile),
          fragment: node.getText(sourceFile)
        });
        
        // Return type approximation (if exists)
        if (node.type) {
           claims.push({
              subject: node.name.text,
              predicate: 'returns_type',
              object: node.type.getText(sourceFile),
              provenance: node.getText(sourceFile)
           });
        }
      }
      
      // 2. Dependency/Call Claims (With Context)
      if (ts.isCallExpression(node)) {
        const expr = node.expression;
        if (ts.isIdentifier(expr)) {
          const caller = findParentScope(node);
          claims.push({
            subject: caller,
            predicate: 'calls',
            object: expr.text,
            provenance: node.getText(sourceFile)
          });
        }
      }

      ts.forEachChild(node, visit);
    };

    visit(sourceFile);
    return claims;
  }

  // KAIROS V3: Structural Scoring
  private kairosScore(raw: RawClaim): number {
    let score = 0;
    
    // Penalize Noise
    if (raw.predicate === 'unknown') score -= 10;
    
    // Reward Structural Definitions
    if (raw.predicate === 'defines_function') score += 10;
    if (raw.predicate === 'defines_class') score += 10;
    
    // Reward Flow Logic
    if (raw.predicate === 'calls') score += 5;
    if (raw.predicate === 'returns_type') score += 5;

    // Penalize Ambiguity
    if ((raw.object || '').includes('TODO')) score -= 15;

    return score;
  }

  private transformToAtomic(raw: RawClaim, sourceId: string): AtomicClaim {
    const safeRaw = RawClaimSchema.parse(raw);
    
    // ID V2: Source + Context + Provenance Hash -> Collision Resistant
    const anchorHash = createHash('sha256').update(safeRaw.provenance).digest('hex').substring(0, 8);
    // e.g. "SourceA:calculateTotal:calls:add:a1b2c3d4"
    const idStr = `${sourceId}:${safeRaw.subject}:${safeRaw.predicate}:${safeRaw.object}:${anchorHash}`;
    const id = createHash('sha256').update(idStr).digest('hex');
    
    const score = this.kairosScore(safeRaw);

    return {
      id,
      sourceId,
      subject: safeRaw.subject,
      predicate: safeRaw.predicate,
      object: safeRaw.object,
      dependencies: safeRaw.dependencies || [],
      payload: {
        anchor: safeRaw.provenance,
        fragment: safeRaw.fragment || safeRaw.provenance
      },
      score
    };
  }

  private deriveEdges(nodes: AtomicClaim[]) {
    const edges: { from: string; to: string; type: RelationshipType }[] = [];
    
    nodes.forEach(node => {
        // Implicit Inference:
        // If "calculateTotal" (node) CALLS "add" (object)
        // And there exists a node where subject="add" AND predicate="defines_function"
        // Then calculateTotal SUPPORTS add (depends on it)
        if (node.predicate === 'calls') {
            const target = nodes.find(n => n.subject === node.object && n.predicate === 'defines_function');
            if (target) {
                edges.push({ from: target.id, to: node.id, type: 'SUPPORTS' });
            }
        }
    });
    
    return edges;
  }
}
