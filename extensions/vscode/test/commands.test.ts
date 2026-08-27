import './vscodeMock';
import * as assert from 'node:assert';
import { describe, it } from 'node:test';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from '../src/cliBridge';
import {
  registerCommands,
  resolveExerciseName,
} from '../src/commands';
import { KubelingsDiagnosticsProvider } from '../src/diagnostics';
import { KubelingsStatusBar } from '../src/statusBar';
import {
  ExerciseTreeItem,
  KubelingsTreeDataProvider,
} from '../src/treeView';
import {
  CliClusterResponse,
  CliHintResponse,
  CliListResponse,
  CliRunResponse,
  CliVerifyResponse,
} from '../src/types';

describe('Kubelings Commands - resolveExerciseName', () => {
  it('resolves string name directly', () => {
    assert.strictEqual(resolveExerciseName('pods01'), 'pods01');
  });

  it('resolves name from ExerciseTreeItem', () => {
    const item = new ExerciseTreeItem(
      {
        name: 'pods02',
        title: 'Pod 2',
        path: 'exercises/01_pods/pods02.py',
        chapter_name: '01_pods',
        requires_cluster: false,
      },
      '/workspace'
    );
    assert.strictEqual(resolveExerciseName(item), 'pods02');
  });

  it('resolves name from Uri', () => {
    const uri = vscode.Uri.file('/workspace/exercises/01_pods/pods03.py');
    assert.strictEqual(resolveExerciseName(uri), 'pods03');
  });
});

describe('Kubelings Commands - Command Registration and Execution', () => {
  class MockFullBridge extends KubelingsCliBridge {
    public async list(): Promise<CliListResponse> {
      return {
        total_chapters: 1,
        total_exercises: 1,
        chapters: [
          {
            number: 1,
            name: '01_pods',
            title: 'Pods Chapter',
            description: 'Pods',
            exercises: [
              {
                name: 'pods01',
                title: 'First Pod',
                path: 'exercises/01_pods/pods01.py',
                solution_path: 'solutions/01_pods/pods01.py',
                chapter_name: '01_pods',
                requires_cluster: false,
                has_not_done: true,
              },
            ],
          },
        ],
      };
    }

    public async run(name: string): Promise<CliRunResponse> {
      return {
        exercise: name,
        passed: true,
        has_not_done_marker: false,
      };
    }

    public async verify(): Promise<CliVerifyResponse> {
      return {
        total: 1,
        completed: 0,
        in_progress: 1,
        not_started: 0,
        percentage: 0,
        next_exercise: 'pods01',
        results: [
          {
            name: 'pods01',
            title: 'First Pod',
            path: 'exercises/01_pods/pods01.py',
            chapter: '01_pods',
            status: 'in_progress',
            passed: false,
            has_not_done_marker: true,
            duration_ms: 20,
          },
        ],
      };
    }

    public async cluster(): Promise<CliClusterResponse> {
      return {
        available: true,
        context: 'kind-kubelings',
        provider: 'kind',
        cluster_mode: 'live',
      };
    }

    public async hint(name: string, index?: number): Promise<CliHintResponse> {
      return {
        exercise: name,
        hint_index: index ?? 0,
        total_hints: 2,
        hint: 'Use apiVersion: v1',
      };
    }
  }

  it('registers all 9 expected extension commands', () => {
    const bridge = new MockFullBridge({ workspaceRoot: '/workspace' });
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

    const expectedCommands = [
      'kubelings.refresh',
      'kubelings.runExercise',
      'kubelings.nextExercise',
      'kubelings.showHint',
      'kubelings.showSolutionDiff',
      'kubelings.startWatch',
      'kubelings.checkCluster',
      'kubelings.testAll',
      'kubelings.openWalkthrough',
    ];

    for (const cmd of expectedCommands) {
      assert.ok(
        (vscode.commands as any).registered.has(cmd),
        `Command ${cmd} was not registered`
      );
    }
  });

  it('executes kubelings.runExercise with success notification', async () => {
    const bridge = new MockFullBridge({ workspaceRoot: '/workspace' });
    const treeDataProvider = new KubelingsTreeDataProvider(bridge);
    const statusBar = new KubelingsStatusBar(bridge);

    const context: any = { subscriptions: [] };
    registerCommands(context, {
      cliBridge: bridge,
      treeDataProvider,
      statusBar,
    });

    let messageShown = '';
    vscode.window.showInformationMessage = async (msg: string) => {
      messageShown = msg;
      return msg;
    };

    await vscode.commands.executeCommand('kubelings.runExercise', 'pods01');
    assert.ok(messageShown.includes("Exercise 'pods01' passed!"));
  });

  it('executes kubelings.checkCluster with connection status notification', async () => {
    const bridge = new MockFullBridge({ workspaceRoot: '/workspace' });
    const treeDataProvider = new KubelingsTreeDataProvider(bridge);
    const statusBar = new KubelingsStatusBar(bridge);

    const context: any = { subscriptions: [] };
    registerCommands(context, {
      cliBridge: bridge,
      treeDataProvider,
      statusBar,
    });

    let messageShown = '';
    vscode.window.showInformationMessage = async (msg: string) => {
      messageShown = msg;
      return msg;
    };

    await vscode.commands.executeCommand('kubelings.checkCluster');
    assert.ok(messageShown.includes('Kubernetes Cluster Connected!'));
    assert.ok(messageShown.includes('kind-kubelings'));
  });

  it('executes kubelings.startWatch and spawns terminal', async () => {
    const bridge = new MockFullBridge({ workspaceRoot: '/workspace' });
    const treeDataProvider = new KubelingsTreeDataProvider(bridge);
    const statusBar = new KubelingsStatusBar(bridge);

    const context: any = { subscriptions: [] };
    registerCommands(context, {
      cliBridge: bridge,
      treeDataProvider,
      statusBar,
    });

    await vscode.commands.executeCommand('kubelings.startWatch');
    const term = (vscode.window as any).terminals.find(
      (t: any) => t.name === 'Kubelings Watch'
    );
    assert.ok(term);
    assert.ok(term.textSent.some((t: string) => t.includes('watch')));
  });

  it('executes kubelings.testAll and spawns test terminal', async () => {
    const bridge = new MockFullBridge({ workspaceRoot: '/workspace' });
    const treeDataProvider = new KubelingsTreeDataProvider(bridge);
    const statusBar = new KubelingsStatusBar(bridge);

    const context: any = { subscriptions: [] };
    registerCommands(context, {
      cliBridge: bridge,
      treeDataProvider,
      statusBar,
    });

    await vscode.commands.executeCommand('kubelings.testAll');
    const term = (vscode.window as any).terminals.find(
      (t: any) => t.name === 'Kubelings Test'
    );
    assert.ok(term);
    assert.ok(term.textSent.some((t: string) => t.includes('test')));
  });
});
