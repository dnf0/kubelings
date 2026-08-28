import * as path from 'path';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from './cliBridge';
import { resolveExercisePath } from './pathUtils';
import { CliChapter, CliExercise } from './types';

/**
 * Tree item representing a curriculum chapter with progress aggregation.
 */
export class ChapterTreeItem extends vscode.TreeItem {
  public readonly chapter: CliChapter;

  constructor(chapter: CliChapter) {
    const formattedNum = String(chapter.number).padStart(2, '0');
    const label = `${formattedNum}: ${chapter.title}`;

    const total = chapter.exercises ? chapter.exercises.length : 0;
    const completed = chapter.exercises
      ? chapter.exercises.filter((ex) => ex.has_not_done === false).length
      : 0;

    const isAllCompleted = total > 0 && completed === total;
    // CollapsibleState: Expanded if active/incomplete or first chapter, Collapsed otherwise
    const collapsibleState =
      isAllCompleted && chapter.number !== 1
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.Expanded;

    super(label, collapsibleState);

    this.chapter = chapter;
    this.contextValue = 'chapterItem';
    this.description = isAllCompleted ? `(${completed}/${total} ✓)` : `(${completed}/${total} ⏳)`;
    this.tooltip = `${chapter.title}\n${chapter.description}\nProgress: ${completed}/${total} Completed`;
    this.iconPath = isAllCompleted
      ? new vscode.ThemeIcon('pass-filled', new vscode.ThemeColor('testing.iconPassed'))
      : new vscode.ThemeIcon('repo');
  }
}

/**
 * Tree item representing an individual Kubelings exercise.
 */
export class ExerciseTreeItem extends vscode.TreeItem {
  public readonly exercise: CliExercise;
  public readonly fullPath: string;

  constructor(exercise: CliExercise, workspaceRoot: string) {
    super(exercise.name, vscode.TreeItemCollapsibleState.None);

    this.exercise = exercise;
    this.fullPath = resolveExercisePath(exercise.path, workspaceRoot);

    this.description = exercise.title;
    this.contextValue = 'exerciseItem';

    let statusText = 'Not Started';
    if (exercise.has_not_done === false) {
      statusText = 'Completed';
      this.iconPath = new vscode.ThemeIcon(
        'pass-filled',
        new vscode.ThemeColor('testing.iconPassed')
      );
    } else if (exercise.has_not_done === true) {
      statusText = 'In Progress';
      this.iconPath = new vscode.ThemeIcon(
        'sync~spin',
        new vscode.ThemeColor('testing.iconQueued')
      );
    } else {
      this.iconPath = new vscode.ThemeIcon('circle-outline');
    }

    this.tooltip = `${exercise.name} - ${exercise.title}\nPath: ${exercise.path}\nStatus: ${statusText}`;

    this.command = {
      command: 'kubelings.openExercise',
      title: 'Open Exercise',
      arguments: [exercise.path, exercise.name],
    };
  }
}

export type KubelingsTreeItem = ChapterTreeItem | ExerciseTreeItem;

/**
 * Tree data provider for the Kubelings Curriculum view.
 */
export class KubelingsTreeDataProvider
  implements vscode.TreeDataProvider<KubelingsTreeItem>
{
  private _onDidChangeTreeData: vscode.EventEmitter<
    KubelingsTreeItem | undefined | null | void
  > = new vscode.EventEmitter<KubelingsTreeItem | undefined | null | void>();
  public readonly onDidChangeTreeData: vscode.Event<
    KubelingsTreeItem | undefined | null | void
  > = this._onDidChangeTreeData.event;

  private cachedChapters: CliChapter[] = [];

  constructor(private cliBridge: KubelingsCliBridge) {}

  public refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  public getTreeItem(element: KubelingsTreeItem): vscode.TreeItem {
    return element;
  }

  public async getChildren(
    element?: KubelingsTreeItem
  ): Promise<KubelingsTreeItem[]> {
    const workspaceRoot = this.cliBridge.getEffectiveWorkspaceRoot();

    if (!element) {
      try {
        const listResponse = await this.cliBridge.list();
        this.cachedChapters = listResponse.chapters || [];
        return this.cachedChapters.map((chapter) => new ChapterTreeItem(chapter));
      } catch (error) {
        return this.cachedChapters.map((chapter) => new ChapterTreeItem(chapter));
      }
    }

    if (element instanceof ChapterTreeItem) {
      return (element.chapter.exercises || []).map(
        (exercise) => new ExerciseTreeItem(exercise, workspaceRoot)
      );
    }

    return [];
  }

  public getCachedChapters(): CliChapter[] {
    return this.cachedChapters;
  }

  public findExercise(exerciseName: string): CliExercise | undefined {
    for (const chapter of this.cachedChapters) {
      const found = chapter.exercises.find((ex) => ex.name === exerciseName);
      if (found) {
        return found;
      }
    }
    return undefined;
  }

  public getAllExercises(): CliExercise[] {
    const result: CliExercise[] = [];
    for (const chapter of this.cachedChapters) {
      result.push(...chapter.exercises);
    }
    return result;
  }
}
