import { PressureReport, GateVerdict, GateAction } from '../core/types';

export class CerberusGatekeeper {
  public evaluate(report: PressureReport, isStyxBound: boolean): GateVerdict {
    if (isStyxBound) return { action: GateAction.REFUSE, reason: 'STYX_BOUND', isFinal: true };
    if (report.isTerminal) return { action: GateAction.REFUSE, reason: 'TERMINAL_PRESSURE', isFinal: true };
    if (report.totalPressure > 0.4) return { action: GateAction.TRIAL, reason: 'HIGH_FRICTION', isFinal: false };
    return { action: GateAction.PASS, reason: 'ADMISSIBLE', isFinal: false };
  }
}
