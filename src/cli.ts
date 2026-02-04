#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { HadesOrchestrator } from './index';

const file = process.argv[2];
if (!file) {
  console.error('usage: hades <file.ts>');
  process.exit(1);
}

const abs = path.resolve(process.cwd(), file);
if (!fs.existsSync(abs)) {
  console.error(`File not found: ${abs}`);
  process.exit(1);
}

const content = fs.readFileSync(abs, 'utf8');

const hades = new HadesOrchestrator();
hades.deliberate(abs, content)
  .then((out) => {
    if (out) process.stdout.write(out + '\n');
  })
  .catch((e) => {
    console.error(String(e));
    process.exit(1);
  });
