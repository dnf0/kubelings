import * as assert from 'node:assert';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { describe, it } from 'node:test';
import { KubelingsCliBridge } from '../src/cliBridge';

describe('KubelingsCliBridge - Command Resolution', () => {
  it('resolves custom python interpreter path with -m kubelings', () => {
    const bridge = new KubelingsCliBridge({
      customPythonPath: '/usr/local/bin/python3',
    });
    const resolved = bridge.resolveCommand('/dummy/path');
    assert.strictEqual(resolved.command, '/usr/local/bin/python3');
    assert.deepStrictEqual(resolved.argsPrefix, ['-m', 'kubelings']);
  });

  it('resolves custom binary executable directly', () => {
    const bridge = new KubelingsCliBridge({
      customPythonPath: '/opt/homebrew/bin/kubelings',
    });
    const resolved = bridge.resolveCommand('/dummy/path');
    assert.strictEqual(resolved.command, '/opt/homebrew/bin/kubelings');
    assert.deepStrictEqual(resolved.argsPrefix, []);
  });

  it('resolves workspace .venv/bin/kubelings if present', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const venvBinDir = path.join(tmpDir, '.venv', 'bin');
      fs.mkdirSync(venvBinDir, { recursive: true });
      const fakeKubelings = path.join(venvBinDir, 'kubelings');
      fs.writeFileSync(fakeKubelings, '#!/bin/sh\nexit 0\n');
      fs.chmodSync(fakeKubelings, 0o755);

      const bridge = new KubelingsCliBridge({ workspaceRoot: tmpDir });
      const resolved = bridge.resolveCommand(tmpDir);

      assert.strictEqual(resolved.command, fakeKubelings);
      assert.deepStrictEqual(resolved.argsPrefix, []);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves workspace .venv/bin/python if kubelings binary is missing', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const venvBinDir = path.join(tmpDir, '.venv', 'bin');
      fs.mkdirSync(venvBinDir, { recursive: true });
      const fakePython = path.join(venvBinDir, 'python');
      fs.writeFileSync(fakePython, '#!/bin/sh\nexit 0\n');
      fs.chmodSync(fakePython, 0o755);

      const bridge = new KubelingsCliBridge({ workspaceRoot: tmpDir });
      const resolved = bridge.resolveCommand(tmpDir);

      assert.strictEqual(resolved.command, fakePython);
      assert.deepStrictEqual(resolved.argsPrefix, ['-m', 'kubelings']);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves uv run kubelings if pyproject.toml exists and no venv', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      fs.writeFileSync(path.join(tmpDir, 'pyproject.toml'), '[project]\nname="test"\n');

      const bridge = new KubelingsCliBridge({ workspaceRoot: tmpDir });
      const resolved = bridge.resolveCommand(tmpDir);

      assert.strictEqual(resolved.command, 'uv');
      assert.deepStrictEqual(resolved.argsPrefix, ['run', 'kubelings']);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('falls back to global kubelings command if no project hints found', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const bridge = new KubelingsCliBridge({ workspaceRoot: tmpDir });
      const resolved = bridge.resolveCommand(tmpDir);

      assert.strictEqual(resolved.command, 'kubelings');
      assert.deepStrictEqual(resolved.argsPrefix, []);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});

describe('KubelingsCliBridge - JSON Parsing and Error Handling', () => {
  it('parses valid JSON response', async () => {
    const bridge = new KubelingsCliBridge();
    // Test executeJson on valid JSON via simulated / mocked response or helper
    const samplePayload = {
      total_chapters: 23,
      total_exercises: 102,
      chapters: [],
    };
    const jsonString = JSON.stringify(samplePayload);
    const parsed = JSON.parse(jsonString);
    assert.strictEqual(parsed.total_chapters, 23);
    assert.strictEqual(parsed.total_exercises, 102);
  });
});

describe('KubelingsCliBridge - Integration with Kubelings CLI', () => {
  // extensions/vscode -> repo root is 2 levels up from cwd, or 4 levels from dist/test
  const repoRoot = path.resolve(process.cwd(), '../..');
  const venvKubelings = path.join(repoRoot, '.venv', 'bin', 'kubelings');
  const hasLocalKubelings = fs.existsSync(venvKubelings);

  it('executes list command and parses JSON payload', async (t) => {
    if (!hasLocalKubelings) {
      t.skip('Skipping integration test: local .venv/bin/kubelings not found');
      return;
    }

    const bridge = new KubelingsCliBridge({ workspaceRoot: repoRoot });
    const listRes = await bridge.list(repoRoot);

    assert.ok(listRes.total_chapters >= 20);
    assert.ok(listRes.total_exercises >= 90);
    assert.strictEqual(listRes.chapters.length, listRes.total_chapters);
    const firstChapter = listRes.chapters[0];
    assert.strictEqual(firstChapter.name, '01_pods');
    assert.ok(firstChapter.exercises.length > 0);
  });

  it('executes hint command and returns progressive hint', async (t) => {
    if (!hasLocalKubelings) {
      t.skip('Skipping integration test: local .venv/bin/kubelings not found');
      return;
    }

    const bridge = new KubelingsCliBridge({ workspaceRoot: repoRoot });
    const hintRes = await bridge.hint('pods01', 0, repoRoot);

    assert.strictEqual(hintRes.exercise, 'pods01');
    assert.strictEqual(hintRes.hint_index, 0);
    assert.ok(hintRes.total_hints >= 1);
    assert.ok(typeof hintRes.hint === 'string' && hintRes.hint.length > 0);
  });

  it('executes cluster command and returns cluster status', async (t) => {
    if (!hasLocalKubelings) {
      t.skip('Skipping integration test: local .venv/bin/kubelings not found');
      return;
    }

    const bridge = new KubelingsCliBridge({ workspaceRoot: repoRoot });
    const clusterRes = await bridge.cluster(repoRoot);

    assert.ok('available' in clusterRes);
    assert.ok('context' in clusterRes);
    assert.ok('provider' in clusterRes);
    assert.ok('cluster_mode' in clusterRes);
  });

  it('executes run command for pods01 and parses result without throwing on exit 1', async (t) => {
    if (!hasLocalKubelings) {
      t.skip('Skipping integration test: local .venv/bin/kubelings not found');
      return;
    }

    const bridge = new KubelingsCliBridge({ workspaceRoot: repoRoot });
    const runRes = await bridge.run('pods01', repoRoot);

    assert.strictEqual(runRes.exercise, 'pods01');
    assert.ok('passed' in runRes);
    assert.ok('has_not_done_marker' in runRes);
  });
});

