import './vscodeMock';
import * as assert from 'node:assert';
import * as fs from 'node:fs';
import * as path from 'node:path';
import { describe, it } from 'node:test';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from '../src/cliBridge';
import { registerCommands } from '../src/commands';
import { KubelingsDiagnosticsProvider } from '../src/diagnostics';
import { KubelingsStatusBar } from '../src/statusBar';
import { KubelingsTreeDataProvider } from '../src/treeView';
import { CliTourResponse } from '../src/types';

describe('Kubelings Walkthrough & Tour Integration', () => {
  const repoRoot = path.resolve(process.cwd(), '../..');
  const venvKubelings = path.join(repoRoot, '.venv', 'bin', 'kubelings');
  const hasLocalKubelings = fs.existsSync(venvKubelings);

  it('bridge resolves tour JSON payload from CLI', async (t) => {
    if (!hasLocalKubelings) {
      t.skip('Skipping integration test: local .venv/bin/kubelings not found');
      return;
    }

    const bridge = new KubelingsCliBridge({ workspaceRoot: repoRoot });
    const tourData: CliTourResponse = await bridge.tour(undefined, repoRoot);

    assert.strictEqual(tourData.total_steps, 5);
    assert.strictEqual(tourData.steps.length, 5);

    const step1 = tourData.steps[0];
    assert.strictEqual(step1.step_num, 1);
    assert.strictEqual(step1.name, 'welcome');
    assert.ok(step1.title.length > 0);
    assert.ok(step1.description.length > 0);

    const step4 = tourData.steps[3];
    assert.strictEqual(step4.step_num, 4);
    assert.strictEqual(step4.name, 'guided_exercise');
  });

  it('bridge supports tour command with specific step parameter', async (t) => {
    if (!hasLocalKubelings) {
      t.skip('Skipping integration test: local .venv/bin/kubelings not found');
      return;
    }

    const bridge = new KubelingsCliBridge({ workspaceRoot: repoRoot });
    const tourData: CliTourResponse = await bridge.tour(2, repoRoot);

    assert.strictEqual(tourData.total_steps, 5);
    assert.strictEqual(tourData.steps.length, 5);
    const step2 = tourData.steps[1];
    assert.strictEqual(step2.name, 'environment');
  });

  it('registers kubelings.openWalkthrough and opens default walkthrough', async () => {
    const bridge = new KubelingsCliBridge({ workspaceRoot: '/workspace' });
    const treeDataProvider = new KubelingsTreeDataProvider(bridge);
    const statusBar = new KubelingsStatusBar(bridge);
    const diagnosticsProvider = new KubelingsDiagnosticsProvider(
      bridge,
      treeDataProvider,
      statusBar
    );

    const context: any = { subscriptions: [] };
    registerCommands(context, {
      cliBridge: bridge,
      treeDataProvider,
      statusBar,
      diagnosticsProvider,
    });

    let executedCommand = '';
    let executedArgs: any[] = [];
    (vscode.commands as any).registered.set(
      'workbench.action.openWalkthrough',
      async (target: string, modal: boolean) => {
        executedCommand = 'workbench.action.openWalkthrough';
        executedArgs = [target, modal];
      }
    );

    await vscode.commands.executeCommand('kubelings.openWalkthrough');
    assert.strictEqual(executedCommand, 'workbench.action.openWalkthrough');
    assert.strictEqual(
      executedArgs[0],
      'dnf0.kubelings-vscode#kubelings.walkthrough'
    );
    assert.strictEqual(executedArgs[1], false);
  });

  it('opens specific step target when stepId is provided to kubelings.openWalkthrough', async () => {
    const bridge = new KubelingsCliBridge({ workspaceRoot: '/workspace' });
    const treeDataProvider = new KubelingsTreeDataProvider(bridge);
    const statusBar = new KubelingsStatusBar(bridge);

    const context: any = { subscriptions: [] };
    registerCommands(context, {
      cliBridge: bridge,
      treeDataProvider,
      statusBar,
    });

    let targetWalkthrough = '';
    (vscode.commands as any).registered.set(
      'workbench.action.openWalkthrough',
      async (target: string, modal: boolean) => {
        targetWalkthrough = target;
      }
    );

    await vscode.commands.executeCommand('kubelings.openWalkthrough', 'exercise');
    assert.strictEqual(
      targetWalkthrough,
      'dnf0.kubelings-vscode#kubelings.walkthrough#exercise'
    );
  });
});
