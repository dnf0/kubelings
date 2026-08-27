import * as vscode from 'vscode';
import { KubelingsCliBridge } from './cliBridge';
import { CliVerifyResponse } from './types';

/**
 * Manages the Kubelings status bar item displaying overall progress and next exercise.
 */
export class KubelingsStatusBar implements vscode.Disposable {
  private statusBarItem: vscode.StatusBarItem;
  private cliBridge: KubelingsCliBridge;
  private lastVerifyData?: CliVerifyResponse;

  constructor(cliBridge: KubelingsCliBridge) {
    this.cliBridge = cliBridge;
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      10
    );
    this.statusBarItem.command = 'kubelings.nextExercise';
    this.statusBarItem.text = '$(symbol-event) Kubelings: Initializing...';
    this.statusBarItem.tooltip = 'Kubelings Interactive Kubernetes Learning';
    this.syncVisibility();
  }

  /**
   * Updates the status bar item text and tooltip with verify results.
   */
  public update(verifyData: CliVerifyResponse): void {
    this.lastVerifyData = verifyData;
    const completed = verifyData.completed ?? 0;
    const total = verifyData.total ?? 0;
    const percentage =
      verifyData.percentage ??
      (total > 0 ? Math.round((completed / total) * 100) : 0);
    const nextExercise = verifyData.next_exercise || 'Complete!';

    this.statusBarItem.text = `$(symbol-event) Kubelings: ${completed}/${total} (${percentage}%) | Next: ${nextExercise}`;
    this.statusBarItem.tooltip = `Kubelings Progress: ${completed}/${total} Completed (${percentage}%)\nClick to open next exercise (${nextExercise})`;
    this.statusBarItem.command = 'kubelings.nextExercise';

    this.syncVisibility();
  }

  /**
   * Executes verification and updates status bar content.
   */
  public async refresh(): Promise<CliVerifyResponse | undefined> {
    try {
      const verifyData = await this.cliBridge.verify();
      this.update(verifyData);
      return verifyData;
    } catch (error) {
      this.statusBarItem.text = '$(symbol-event) Kubelings: Ready';
      this.statusBarItem.tooltip = 'Kubelings: Click to open next exercise';
      this.syncVisibility();
      return undefined;
    }
  }

  /**
   * Synchronizes visibility based on configuration.
   */
  public syncVisibility(): void {
    const config = vscode.workspace.getConfiguration('kubelings');
    const showStatusBar = config.get<boolean>('showStatusBar', true);
    if (showStatusBar) {
      this.statusBarItem.show();
    } else {
      this.statusBarItem.hide();
    }
  }

  public show(): void {
    this.statusBarItem.show();
  }

  public hide(): void {
    this.statusBarItem.hide();
  }

  public dispose(): void {
    this.statusBarItem.dispose();
  }

  public getStatusBarItem(): vscode.StatusBarItem {
    return this.statusBarItem;
  }

  public getLastVerifyData(): CliVerifyResponse | undefined {
    return this.lastVerifyData;
  }
}
