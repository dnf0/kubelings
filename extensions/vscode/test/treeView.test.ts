import './vscodeMock';
import * as assert from 'node:assert';
import { describe, it } from 'node:test';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from '../src/cliBridge';
import {
  ChapterTreeItem,
  ExerciseTreeItem,
  KubelingsTreeDataProvider,
} from '../src/treeView';
import { CliChapter, CliExercise, CliListResponse } from '../src/types';

describe('Kubelings Tree View - ChapterTreeItem', () => {
  const sampleChapterIncomplete: CliChapter = {
    number: 1,
    name: '01_pods',
    title: 'Kubernetes Core Workloads & Pods',
    description: 'First chapter on Pods',
    exercises: [
      {
        name: 'pods01',
        title: 'First Pod Manifest',
        path: 'exercises/01_pods/pods01.py',
        chapter_name: '01_pods',
        requires_cluster: false,
        has_not_done: false, // completed
      },
      {
        name: 'pods02',
        title: 'Multi Container Pod',
        path: 'exercises/01_pods/pods02.py',
        chapter_name: '01_pods',
        requires_cluster: false,
        has_not_done: true, // in progress
      },
    ],
  };

  const sampleChapterCompleted: CliChapter = {
    number: 2,
    name: '02_controllers',
    title: 'Deployments & Controllers',
    description: 'Second chapter',
    exercises: [
      {
        name: 'deploy01',
        title: 'Deployment Spec',
        path: 'exercises/02_controllers/deploy01.py',
        chapter_name: '02_controllers',
        requires_cluster: false,
        has_not_done: false, // completed
      },
    ],
  };

  it('formats chapter label with zero-padded number and title', () => {
    const item = new ChapterTreeItem(sampleChapterIncomplete);
    assert.strictEqual(item.label, '01: Kubernetes Core Workloads & Pods');
    assert.strictEqual(item.contextValue, 'chapterItem');
  });

  it('displays in-progress count in description for incomplete chapters', () => {
    const item = new ChapterTreeItem(sampleChapterIncomplete);
    assert.strictEqual(item.description, '(1/2 ⏳)');
    assert.strictEqual(
      item.collapsibleState,
      vscode.TreeItemCollapsibleState.Expanded
    );
  });

  it('displays completion tick in description for completed chapters and collapses if chapter > 1', () => {
    const item = new ChapterTreeItem(sampleChapterCompleted);
    assert.strictEqual(item.description, '(1/1 ✓)');
    assert.strictEqual(
      item.collapsibleState,
      vscode.TreeItemCollapsibleState.Collapsed
    );
  });

  it('includes comprehensive tooltip information', () => {
    const item = new ChapterTreeItem(sampleChapterIncomplete);
    const tooltip = String(item.tooltip || '');
    assert.ok(tooltip.includes('Kubernetes Core Workloads & Pods'));
    assert.ok(tooltip.includes('Progress: 1/2 Completed'));
  });
});

describe('Kubelings Tree View - ExerciseTreeItem', () => {
  const workspaceRoot = '/test/workspace';

  const completedEx: CliExercise = {
    name: 'pods01',
    title: 'First Pod Manifest',
    path: 'exercises/01_pods/pods01.py',
    solution_path: 'solutions/01_pods/pods01.py',
    chapter_name: '01_pods',
    requires_cluster: false,
    has_not_done: false,
  };

  const inProgressEx: CliExercise = {
    name: 'pods02',
    title: 'Multi Container Pod',
    path: 'exercises/01_pods/pods02.py',
    chapter_name: '01_pods',
    requires_cluster: false,
    has_not_done: true,
  };

  const notStartedEx: CliExercise = {
    name: 'pods03',
    title: 'Init Containers',
    path: 'exercises/01_pods/pods03.py',
    chapter_name: '01_pods',
    requires_cluster: false,
  };

  it('configures completed exercise item with pass icon', () => {
    const item = new ExerciseTreeItem(completedEx, workspaceRoot);
    assert.strictEqual(item.label, 'pods01');
    assert.strictEqual(item.description, 'First Pod Manifest');
    assert.strictEqual(item.contextValue, 'exerciseItem');
    const icon = item.iconPath as vscode.ThemeIcon;
    assert.strictEqual(icon.id, 'pass-filled');
    const tooltip = String(item.tooltip || '');
    assert.ok(tooltip.includes('Status: Completed'));
    assert.strictEqual(item.command?.command, 'vscode.open');
    assert.strictEqual(
      item.command?.arguments?.[0]?.fsPath,
      '/test/workspace/exercises/01_pods/pods01.py'
    );
  });

  it('configures in-progress exercise item with queued sync icon', () => {
    const item = new ExerciseTreeItem(inProgressEx, workspaceRoot);
    const icon = item.iconPath as vscode.ThemeIcon;
    assert.strictEqual(icon.id, 'sync~spin');
    const tooltip = String(item.tooltip || '');
    assert.ok(tooltip.includes('Status: In Progress'));
  });

  it('configures not started exercise item with circle outline icon', () => {
    const item = new ExerciseTreeItem(notStartedEx, workspaceRoot);
    const icon = item.iconPath as vscode.ThemeIcon;
    assert.strictEqual(icon.id, 'circle-outline');
    const tooltip = String(item.tooltip || '');
    assert.ok(tooltip.includes('Status: Not Started'));
  });
});

describe('Kubelings Tree View - KubelingsTreeDataProvider', () => {
  const mockChapters: CliChapter[] = [
    {
      number: 1,
      name: '01_pods',
      title: 'Pod Workloads',
      description: 'Pods chapter',
      exercises: [
        {
          name: 'pods01',
          title: 'First Pod',
          path: 'exercises/01_pods/pods01.py',
          chapter_name: '01_pods',
          requires_cluster: false,
          has_not_done: false,
        },
      ],
    },
  ];

  class MockBridge extends KubelingsCliBridge {
    public async list(): Promise<CliListResponse> {
      return {
        total_chapters: 1,
        total_exercises: 1,
        chapters: mockChapters,
      };
    }
  }

  it('retrieves root chapter items when element is undefined', async () => {
    const bridge = new MockBridge({ workspaceRoot: '/test/workspace' });
    const provider = new KubelingsTreeDataProvider(bridge);

    const roots = await provider.getChildren();
    assert.strictEqual(roots.length, 1);
    assert.ok(roots[0] instanceof ChapterTreeItem);
    assert.strictEqual(
      (roots[0] as ChapterTreeItem).chapter.name,
      '01_pods'
    );
  });

  it('retrieves child exercise items for a given chapter item', async () => {
    const bridge = new MockBridge({ workspaceRoot: '/test/workspace' });
    const provider = new KubelingsTreeDataProvider(bridge);

    const chapterItem = new ChapterTreeItem(mockChapters[0]);
    const children = await provider.getChildren(chapterItem);

    assert.strictEqual(children.length, 1);
    assert.ok(children[0] instanceof ExerciseTreeItem);
    assert.strictEqual(
      (children[0] as ExerciseTreeItem).exercise.name,
      'pods01'
    );
  });

  it('returns empty array when children requested for an exercise item', async () => {
    const bridge = new MockBridge({ workspaceRoot: '/test/workspace' });
    const provider = new KubelingsTreeDataProvider(bridge);

    const exItem = new ExerciseTreeItem(
      mockChapters[0].exercises[0],
      '/test/workspace'
    );
    const children = await provider.getChildren(exItem);
    assert.deepStrictEqual(children, []);
  });

  it('fires onDidChangeTreeData event on refresh', async () => {
    const bridge = new MockBridge({ workspaceRoot: '/test/workspace' });
    const provider = new KubelingsTreeDataProvider(bridge);

    let fired = false;
    provider.onDidChangeTreeData(() => {
      fired = true;
    });

    provider.refresh();
    assert.strictEqual(fired, true);
  });

  it('finds cached exercise by name', async () => {
    const bridge = new MockBridge({ workspaceRoot: '/test/workspace' });
    const provider = new KubelingsTreeDataProvider(bridge);

    await provider.getChildren(); // populates cache
    const found = provider.findExercise('pods01');
    assert.ok(found);
    assert.strictEqual(found?.name, 'pods01');
    assert.strictEqual(provider.findExercise('nonexistent'), undefined);
  });
});
