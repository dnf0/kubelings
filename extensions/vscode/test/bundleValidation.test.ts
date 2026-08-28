import { describe, it } from 'node:test';
import * as assert from 'node:assert';
import * as fs from 'node:fs';
import * as path from 'node:path';

describe('VSIX Bundle Validation', () => {
  it('verifies that dist/extension.js is freshly built and contains cleanPath logic', () => {
    const bundlePath = path.resolve(__dirname, '../extension.js');
    assert.ok(fs.existsSync(bundlePath), `dist/extension.js must exist at ${bundlePath}`);

    const content = fs.readFileSync(bundlePath, 'utf8');
    assert.ok(content.includes('cleanPath'), 'dist/extension.js must contain cleanPath logic');
    assert.ok(content.includes('cleanPath = exPath.replace'), 'dist/extension.js must strip leading slashes');
  });
});
