import './vscodeMock';
import * as assert from 'node:assert';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { describe, it } from 'node:test';
import {
  getCandidateFilePaths,
  getEffectiveWorkspaceRoot,
  resolveExercisePath,
} from '../src/pathUtils';

describe('Kubelings pathUtils - getEffectiveWorkspaceRoot', () => {
  it('returns explicit root if passed', () => {
    const root = getEffectiveWorkspaceRoot('/custom/explicit/path');
    assert.strictEqual(root, '/custom/explicit/path');
  });

  it('never returns root "/" or empty string', () => {
    const root = getEffectiveWorkspaceRoot();
    assert.notStrictEqual(root, '/');
    assert.notStrictEqual(root, '\\');
    assert.notStrictEqual(root, '/exercises');
    assert.ok(root.length > 0);
  });

  it('rejects root "/" even if passed as explicitRoot', () => {
    const root = getEffectiveWorkspaceRoot('/');
    assert.notStrictEqual(root, '/');
    assert.ok(root.includes('kubelings'));
  });
});

describe('Kubelings pathUtils - getCandidateFilePaths', () => {
  it('prioritizes .yaml over .yml and .py', () => {
    const candidates = getCandidateFilePaths('exercises/01_pods/pods01.yaml');
    assert.strictEqual(candidates[0], 'exercises/01_pods/pods01.yaml');
    assert.strictEqual(candidates[1], 'exercises/01_pods/pods01.yml');
    assert.strictEqual(candidates[2], 'exercises/01_pods/pods01.py');
  });

  it('generates .yaml first even when given .py path', () => {
    const candidates = getCandidateFilePaths('exercises/01_pods/pods01.py');
    assert.strictEqual(candidates[0], 'exercises/01_pods/pods01.yaml');
    assert.strictEqual(candidates[1], 'exercises/01_pods/pods01.yml');
    assert.strictEqual(candidates[2], 'exercises/01_pods/pods01.py');
  });

  it('appends extensions when given extensionless path', () => {
    const candidates = getCandidateFilePaths('exercises/01_pods/pods01');
    assert.strictEqual(candidates[0], 'exercises/01_pods/pods01.yaml');
    assert.strictEqual(candidates[1], 'exercises/01_pods/pods01.yml');
    assert.strictEqual(candidates[2], 'exercises/01_pods/pods01.py');
  });
});

describe('Kubelings pathUtils - resolveExercisePath', () => {
  it('resolves directly when file exists in root workspace', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const exDir = path.join(tmpDir, 'exercises', '01_pods');
      fs.mkdirSync(exDir, { recursive: true });
      const exFile = path.join(exDir, 'pods01.yaml');
      fs.writeFileSync(exFile, '# test exercise');

      const resolved = resolveExercisePath('exercises/01_pods/pods01.yaml', tmpDir);
      assert.strictEqual(resolved, exFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves .yaml file when .py path is requested and .yaml exists on disk', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const exDir = path.join(tmpDir, 'exercises', '01_pods');
      fs.mkdirSync(exDir, { recursive: true });
      const exFile = path.join(exDir, 'pods01.yaml');
      fs.writeFileSync(exFile, '# test exercise');

      const resolved = resolveExercisePath('exercises/01_pods/pods01.py', tmpDir);
      assert.strictEqual(resolved, exFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves stripped path when workspace is inside exercises/ directory', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const exercisesDir = path.join(tmpDir, 'exercises');
      const exDir = path.join(exercisesDir, '01_pods');
      fs.mkdirSync(exDir, { recursive: true });
      const exFile = path.join(exDir, 'pods01.yaml');
      fs.writeFileSync(exFile, '# test exercise');

      // Workspace root is /tmp/.../exercises
      const resolved = resolveExercisePath(
        'exercises/01_pods/pods01.yaml',
        exercisesDir
      );
      assert.strictEqual(resolved, exFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves basename when workspace is inside individual chapter directory', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const chapterDir = path.join(tmpDir, 'exercises', '01_pods');
      fs.mkdirSync(chapterDir, { recursive: true });
      const exFile = path.join(chapterDir, 'pods01.yaml');
      fs.writeFileSync(exFile, '# test exercise');

      // Workspace root is /tmp/.../exercises/01_pods
      const resolved = resolveExercisePath(
        'exercises/01_pods/pods01.yaml',
        chapterDir
      );
      assert.strictEqual(resolved, exFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves by ascending parent directory traversal from subfolder', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const repoRoot = path.join(tmpDir, 'repo');
      const exercisesDir = path.join(repoRoot, 'exercises', '01_pods');
      const subfolder = path.join(repoRoot, 'extensions', 'vscode');
      fs.mkdirSync(exercisesDir, { recursive: true });
      fs.mkdirSync(subfolder, { recursive: true });

      const exFile = path.join(exercisesDir, 'pods01.yaml');
      fs.writeFileSync(exFile, '# test exercise');

      // Workspace root is extensions/vscode (2 levels down)
      const resolved = resolveExercisePath(
        'exercises/01_pods/pods01.yaml',
        subfolder
      );
      assert.strictEqual(resolved, exFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves solution path correctly across structures', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const solDir = path.join(tmpDir, 'solutions', '01_pods');
      fs.mkdirSync(solDir, { recursive: true });
      const solFile = path.join(solDir, 'pods01.yaml');
      fs.writeFileSync(solFile, '# test solution');

      const resolved = resolveExercisePath('solutions/01_pods/pods01.yaml', tmpDir);
      assert.strictEqual(resolved, solFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });

  it('resolves exercise from standard directory when root is invalid', () => {
    const resolved = resolveExercisePath('exercises/01_pods/pods01.yaml', '/');
    assert.ok(fs.existsSync(resolved));
    assert.ok(resolved.endsWith(path.join('01_pods', 'pods01.yaml')));
  });

  it('resolves exercise with leading slash correctly', () => {
    const resolved = resolveExercisePath('/exercises/01_pods/pods01.yaml', '/');
    assert.ok(fs.existsSync(resolved));
    assert.ok(resolved.endsWith(path.join('01_pods', 'pods01.yaml')));
    assert.notStrictEqual(resolved, '/exercises/01_pods/pods01.yaml');
  });
});

