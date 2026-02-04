
import { describe, it, expect } from 'vitest';
import { HadesOrchestrator } from './index';

describe('HadesOrchestrator', () => {
  it('should instantiate', () => {
    const hades = new HadesOrchestrator();
    expect(hades).toBeDefined();
  });
});
