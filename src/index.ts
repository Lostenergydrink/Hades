import { HecateDecomposer } from './pillars/Hecate';
import { ErisPressureCalculator } from './pillars/Eris';
import { StyxStore } from './pillars/Styx';
import { CerberusGatekeeper } from './pillars/Cerberus';
import { PersephoneSandbox } from './pillars/Persephone';
import { MoiraeWeaver } from './pillars/Moirae';
import { LetheArchive } from './pillars/Lethe';
import { GateAction, AssertionGraph, PressureReport, GateVerdict, TrialVerdict } from './core/types';
import pino from 'pino';
import fs from 'node:fs';
import path from 'node:path';

const logger = pino({ 
    transport: { target: 'pino-pretty' },
    level: 'info'
});

export interface DeliberationArtifacts {
  graph: AssertionGraph;
  pressure: PressureReport;
  gateVerdict: GateVerdict;
  trialVerdict?: TrialVerdict;
  woven?: string;
}

export class HadesOrchestrator {
  constructor(
    private hecate = new HecateDecomposer(),
    private eris = new ErisPressureCalculator(),
    private styx = new StyxStore(),
    private lethe = new LetheArchive(),
    private cerberus = new CerberusGatekeeper(),
    private persephone = new PersephoneSandbox(),
    private moirae = new MoiraeWeaver(),
    private artifactsDir = './artifacts'
  ) {}

  private writeArtifact(name: string, data: unknown): void {
    if (!fs.existsSync(this.artifactsDir)) {
      fs.mkdirSync(this.artifactsDir, { recursive: true });
    }
    const filePath = path.join(this.artifactsDir, name);
    const content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    fs.writeFileSync(filePath, content, 'utf8');
    logger.debug({ msg: 'Artifact written', path: filePath });
  }

  public async deliberate(inputSource: string, content: string): Promise<string | undefined> {
    logger.info({ msg: 'Intake', source: inputSource });

    // 1. Decompose (Real AST with Context)
    const graph = this.hecate.decompose(inputSource, content);
    logger.info({ msg: 'Assertion Graph', nodes: graph.nodes.length });
    this.writeArtifact('graph.json', graph);

    if (graph.nodes.length === 0) {
        logger.error("EPISTEMIC_COLLAPSE: No valid claims extracted.");
        return;
    }
    
    // 2. Styx Check
    if (this.styx.isBound(graph)) throw new Error('STYX_BOUND');

    // 3. Pressure
    const report = this.eris.calculatePressure(graph);
    logger.info({ msg: 'Pressure Report', pressure: report.totalPressure, conflicts: report.conflictMap });
    this.writeArtifact('pressure.json', report);

    // 4. Gate
    const verdict = this.cerberus.evaluate(report, false);
    let trialVerdict: TrialVerdict | undefined;

    if (verdict.action === GateAction.REFUSE) {
      this.styx.swearOath(graph);
      this.lethe.recordFailure(graph);
      this.writeArtifact('verdict.json', { gate: verdict });
      throw new Error(`REFUSED: ${verdict.reason}`);
    }

    if (verdict.action === GateAction.TRIAL) {
      trialVerdict = await this.persephone.administerOrdeal(graph, report.conflictMap);
      this.writeArtifact('verdict.json', { gate: verdict, trial: trialVerdict });
      if (!trialVerdict.success) {
        this.styx.swearOath(graph);
        throw new Error(`TRIAL_FAILED: ${trialVerdict.outcome}`);
      }
    } else {
      this.writeArtifact('verdict.json', { gate: verdict });
    }

    // 5. Weave
    const survivedIds = new Set(graph.nodes.map(n => n.id));
    const woven = this.moirae.weave(graph, survivedIds);
    this.writeArtifact('artifact.txt', woven);
    
    return woven;
  }
}

// Export for library usage
export { HecateDecomposer } from './pillars/Hecate';
export { ErisPressureCalculator } from './pillars/Eris';
export { StyxStore } from './pillars/Styx';
export { CerberusGatekeeper } from './pillars/Cerberus';
export { PersephoneSandbox } from './pillars/Persephone';
export { MoiraeWeaver } from './pillars/Moirae';
export { LetheArchive } from './pillars/Lethe';
export * from './core/types';
