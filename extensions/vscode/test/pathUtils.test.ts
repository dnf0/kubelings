import './vscodeMock';
import * as assert from 'node:assert';
import * as fs from 'node:fs';
import * as os from 'node:os';
import * as path from 'node:path';
import { describe, it } from 'node:test';
import { getEffectiveWorkspaceRoot, resolveExercisePath } from '../src/pathUtils';

describe('Kubelings pathUtils - getEffectiveWorkspaceRoot', () => {
  it('returns explicit root if passed', () => {
    const root = getEffectiveWorkspaceRoot('/custom/explicit/path');
    assert.strictEqual(root, '/custom/explicit/path');
  });

  it('never returns root "/" or empty string', () => {
    const root = getEffectiveWorkspaceRoot();
    assert.notStrictEqual(root, '/');
    assert.notStrictEqual(root, '\\');
    assert.ok(root.length > 0);
  });
});

describe('Kubelings pathUtils - resolveExercisePath', () => {
  it('resolves directly when file exists in root workspace', () => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kubelings-test-'));
    try {
      const exDir = path.join(tmpDir, 'exercises', '01_pods');
      fs.mkdirSync(exDir, { recursive: true });
      const exFile = path.join(exDir, 'pods01.py');
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
      const exFile = path.join(exDir, 'pods01.py');
      fs.writeFileSync(exFile, '# test exercise');

      // Workspace root is /tmp/.../exercises
      const resolved = resolveExercisePath(
        'exercises/01_pods/pods01.py',
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
      const exFile = path.join(chapterDir, 'pods01.py');
      fs.writeFileSync(exFile, '# test exercise');

      // Workspace root is /tmp/.../exercises/01_pods
      const resolved = resolveExercisePath(
        'exercises/01_pods/pods01.py',
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

      const exFile = path.join(exercisesDir, 'pods01.py');
      fs.writeFileSync(exFile, '# test exercise');

      // Workspace root is extensions/vscode (2 levels down)
      const resolved = resolveExercisePath(
        'exercises/01_pods/pods01.py',
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
      const solFile = path.join(solDir, 'pods01.py');
      fs.writeFileSync(solFile, '# test solution');

      const resolved = resolveExercisePath('solutions/01_pods/pods01.py', tmpDir);
      assert.strictEqual(resolved, solFile);
    } finally {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});
