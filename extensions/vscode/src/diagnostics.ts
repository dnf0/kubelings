import * as path from 'path';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from './cliBridge';
import { KubelingsStatusBar } from './statusBar';
import { KubelingsTreeDataProvider } from './treeView';
import { CliRunResponse } from './types';

/**
 * Diagnostics provider managing inline editor problem markers when exercises fail.
 */
export class KubelingsDiagnosticsProvider implements vscode.Disposable {
  private diagnosticCollection: vscode.DiagnosticCollection;
  private cliBridge: KubelingsCliBridge;
  private treeDataProvider?: KubelingsTreeDataProvider;
  private statusBar?: KubelingsStatusBar;

  constructor(
    cliBridge: KubelingsCliBridge,
    treeDataProvider?: KubelingsTreeDataProvider,
    statusBar?: KubelingsStatusBar
  ) {
    this.cliBridge = cliBridge;
    this.treeDataProvider = treeDataProvider;
    this.statusBar = statusBar;
    this.diagnosticCollection =
      vscode.languages.createDiagnosticCollection('kubelings');
  }

  /**
   * Evaluates an exercise document upon save and updates diagnostics.
   */
  public async handleDocumentSave(
    document: vscode.TextDocument
  ): Promise<CliRunResponse | undefined> {
    if (document.uri.scheme !== 'file') {
      return undefined;
    }

    const normalizedPath = document.fileName.replace(/\\/g, '/');
    if (!/\.(yaml|yml|py)$/i.test(normalizedPath)) {
      return undefined;
    }

    const exerciseName = path.basename(normalizedPath).replace(/\.(yaml|yml|py)$/i, '');
    const isExerciseFile =
      normalizedPath.includes('/exercises/') ||
      this.treeDataProvider?.findExercise(exerciseName) !== undefined;

    if (!isExerciseFile) {
      return undefined;
    }

    try {
      const runResult = await this.cliBridge.run(exerciseName);

      if (runResult.passed) {
        this.diagnosticCollection.delete(document.uri);
        this.treeDataProvider?.refresh();
        this.statusBar?.refresh().catch(() => {});
        return runResult;
      }

      // Exercise failed validation checks
      const text = document.getText();
      const lines = text.split(/\r?\n/);

      let targetLine = 0;
      if (
        runResult.error_line !== undefined &&
        runResult.error_line !== null &&
        runResult.error_line > 0
      ) {
        targetLine = Math.min(
          Math.max(0, runResult.error_line - 1),
          lines.length - 1
        );
      }

      const lineText = lines[targetLine] || '';
      const range = new vscode.Range(
        new vscode.Position(targetLine, 0),
        new vscode.Position(targetLine, Math.max(lineText.length, 1))
      );

      const message = `[Kubelings] ${
        runResult.error && runResult.error.trim().length > 0
          ? runResult.error.trim()
          : 'Exercise validation failed.'
      }`;

      const diagnostic = new vscode.Diagnostic(
        range,
        message,
        vscode.DiagnosticSeverity.Error
      );
      diagnostic.source = 'kubelings';
      diagnostic.code = exerciseName;

      this.diagnosticCollection.set(document.uri, [diagnostic]);
      this.treeDataProvider?.refresh();
      this.statusBar?.refresh().catch(() => {});

      return runResult;
    } catch (err) {
      return undefined;
    }
  }

  public clear(): void {
    this.diagnosticCollection.clear();
  }

  public dispose(): void {
    this.diagnosticCollection.dispose();
  }

  public getDiagnosticCollection(): vscode.DiagnosticCollection {
    return this.diagnosticCollection;
  }
}

/**
 * Code action provider registering QuickFix hints and solution diff actions for Kubelings diagnostics.
 */
export class KubelingsCodeActionProvider implements vscode.CodeActionProvider {
  public static readonly providedCodeActionKinds = [
    vscode.CodeActionKind.QuickFix,
  ];

  public provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range | vscode.Selection,
    context: vscode.CodeActionContext
  ): vscode.CodeAction[] {
    const kubelingsDiagnostics = context.diagnostics.filter(
      (d) => d.source === 'kubelings'
    );

    if (kubelingsDiagnostics.length === 0) {
      return [];
    }

    const normalizedPath = document.fileName.replace(/\\/g, '/');
    const exerciseName = path.basename(normalizedPath).replace(/\.(yaml|yml|py)$/i, '');

    const actions: vscode.CodeAction[] = [];

    // 💡 Kubelings: Reveal Hint
    const hintAction = new vscode.CodeAction(
      '💡 Kubelings: Reveal Hint',
      vscode.CodeActionKind.QuickFix
    );
    hintAction.command = {
      command: 'kubelings.showHint',
      title: 'Kubelings: Show Hint',
      arguments: [exerciseName],
    };
    hintAction.diagnostics = kubelingsDiagnostics;
    hintAction.isPreferred = true;
    actions.push(hintAction);

    // 🔍 Kubelings: Compare with Reference Solution
    const diffAction = new vscode.CodeAction(
      '🔍 Kubelings: Compare with Reference Solution',
      vscode.CodeActionKind.QuickFix
    );
    diffAction.command = {
      command: 'kubelings.showSolutionDiff',
      title: 'Kubelings: Compare with Reference Solution',
      arguments: [exerciseName],
    };
    diffAction.diagnostics = kubelingsDiagnostics;
    actions.push(diffAction);

    return actions;
  }
}
