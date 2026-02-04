import { LetheReport } from '../core/types';

export class LetheArchive {
  public calculateFriction(graph: unknown): LetheReport { 
      return { friction: 0, applied: false, reasons: ["NOT_IMPLEMENTED"] }; 
  }
  public recordFailure(graph: unknown): void {}
}
