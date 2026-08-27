import * as vscode from 'vscode';
import { KubelingsCliBridge } from './cliBridge';
import { registerCommands } from './commands';
import {
  KubelingsCodeActionProvider,
  KubelingsDiagnosticsProvider,
} from './diagnostics';
import { KubelingsStatusBar } from './statusBar';
import { KubelingsTreeDataProvider } from './treeView';

export function activate(context: vscode.ExtensionContext): void {
  const cliBridge = new KubelingsCliBridge();
  const treeDataProvider = new KubelingsTreeDataProvider(cliBridge);
  const statusBar = new KubelingsStatusBar(cliBridge);
  const diagnosticsProvider = new KubelingsDiagnosticsProvider(
    cliBridge,
    treeDataProvider,
    statusBar
  );
  const codeActionProvider = new KubelingsCodeActionProvider();

  // 1. Register Curriculum Tree View
  const treeView = vscode.window.registerTreeDataProvider(
    'kubelings.curriculumView',
    treeDataProvider
  );
  context.subscriptions.push(treeView);

  // 2. Register Python Code Actions Provider
  const codeActions = vscode.languages.registerCodeActionsProvider(
    { language: 'python' },
    codeActionProvider,
    {
      providedCodeActionKinds:
        KubelingsCodeActionProvider.providedCodeActionKinds,
    }
  );
  context.subscriptions.push(codeActions);

  // 3. Register Diagnostics Provider & Status Bar
  context.subscriptions.push(diagnosticsProvider);
  context.subscriptions.push(statusBar);

  // 4. Register All Extension Commands
  registerCommands(context, {
    cliBridge,
    treeDataProvider,
    statusBar,
    diagnosticsProvider,
  });

  // 5. Auto-run and Validate on Exercise Document Save
  const saveListener = vscode.workspace.onDidSaveTextDocument((document) => {
    const config = vscode.workspace.getConfiguration('kubelings');
    const runOnSave = config.get<boolean>('runOnSave', true);
    if (runOnSave) {
      diagnosticsProvider.handleDocumentSave(document).catch(() => {});
    }
  });
  context.subscriptions.push(saveListener);

  // 6. Handle Configuration Updates (Status Bar Visibility, etc.)
  const configListener = vscode.workspace.onDidChangeConfiguration((e) => {
    if (e.affectsConfiguration('kubelings.showStatusBar')) {
      statusBar.syncVisibility();
    }
  });
  context.subscriptions.push(configListener);

  // 7. Initial Data Fetch & Refresh
  treeDataProvider.refresh();
  statusBar.refresh().catch(() => {});
}

export function deactivate(): void {
  // All resources registered with context.subscriptions are automatically disposed
}
