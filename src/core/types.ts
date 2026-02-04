export type RelationshipType = 'SUPPORTS' | 'CONTRADICTS' | 'REFINES';

export interface AtomicClaim {
  readonly id: string;
  readonly sourceId: string;
  readonly subject: string;
  readonly predicate: string;
  readonly object: string;
  readonly dependencies: string[];
  readonly payload: {
    anchor: string;   // The raw text for audit (The "Why")
    fragment: string; // The clean artifact for assembly (The "What")
  };
  readonly score: number; // Kairos score
}

export interface AssertionGraph {
  readonly nodes: AtomicClaim[];
  readonly edges: { from: string; to: string; type: RelationshipType }[];
}

export interface PressureReport {
  readonly totalPressure: number;
  readonly conflictMap: Record<string, string[]>;
  readonly isTerminal: boolean;
  readonly reasonCodes: string[];
}

export enum GateAction {
  PASS = 'PASS',
  REFUSE = 'REFUSE',
  TRIAL = 'TRIAL'
}

export interface GateVerdict {
  action: GateAction;
  reason: string;
  isFinal: boolean;
}

export enum TrialOutcome {
  RE_DERIVATION_MATCH = 'RE_DERIVATION_MATCH',
  RE_DERIVATION_DIVERGED = 'RE_DERIVATION_DIVERGED',
  PROVENANCE_FAIL = 'PROVENANCE_FAIL',
  FORMALIZATION_FAIL = 'FORMALIZATION_FAIL'
}

export interface TrialVerdict {
  outcome: TrialOutcome;
  success: boolean;
}

export interface LetheReport {
  friction: number;
  applied: boolean;
  reasons: string[];
}
