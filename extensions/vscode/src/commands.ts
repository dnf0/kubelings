import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from './cliBridge';
import { KubelingsDiagnosticsProvider } from './diagnostics';
import { resolveExercisePath } from './pathUtils';
import { KubelingsStatusBar } from './statusBar';
import { ExerciseTreeItem, KubelingsTreeDataProvider } from './treeView';

export interface CommandContext {
  cliBridge: KubelingsCliBridge;
  treeDataProvider: KubelingsTreeDataProvider;
  statusBar: KubelingsStatusBar;
  diagnosticsProvider?: KubelingsDiagnosticsProvider;
}

/**
 * Helper to resolve the target exercise name from command arguments or active editor.
 */
export function resolveExerciseName(
  arg?: ExerciseTreeItem | string | vscode.Uri | unknown
): string | undefined {
  if (typeof arg === 'string' && arg.trim().length > 0) {
    const trimmed = arg.trim();
    const base = path.basename(trimmed).replace(/\.(yaml|yml|py)$/i, '');
    return base || trimmed;
  }

  if (arg instanceof ExerciseTreeItem) {
    return arg.exercise.name;
  }

  if (arg && typeof arg === 'object' && 'exercise' in arg) {
    const item = arg as ExerciseTreeItem;
    if (item.exercise?.name) {
      return item.exercise.name;
    }
  }

  if (arg && typeof arg === 'object' && 'fsPath' in arg) {
    const uri = arg as vscode.Uri;
    const base = path.basename(uri.fsPath).replace(/\.(yaml|yml|py)$/i, '');
    if (base) {
      return base;
    }
  }

  const activeEditor = vscode.window.activeTextEditor;
  if (activeEditor) {
    const activeFile = activeEditor.document.fileName;
    if (/\.(yaml|yml|py)$/i.test(activeFile)) {
      return path.basename(activeFile).replace(/\.(yaml|yml|py)$/i, '');
    }
  }

  return undefined;
}

/**
 * Registers all Kubelings VS Code commands.
 */
export function registerCommands(
  context: vscode.ExtensionContext,
  services: CommandContext
): void {
  const { cliBridge, treeDataProvider, statusBar } = services;

  // 1. kubelings.refresh
  const refreshCmd = vscode.commands.registerCommand(
    'kubelings.refresh',
    async () => {
      treeDataProvider.refresh();
      await statusBar.refresh();
    }
  );
  context.subscriptions.push(refreshCmd);

/**
 * Helper to prompt the user for a workspace folder if no folder is currently open.
 */
async function getOrSelectWorkspaceFolder(): Promise<string | undefined> {
  if (
    vscode.workspace.workspaceFolders &&
    vscode.workspace.workspaceFolders.length > 0
  ) {
    const fsPath = vscode.workspace.workspaceFolders[0].uri.fsPath;
    if (
      fsPath &&
      fsPath !== '/' &&
      fsPath !== '\\' &&
      fsPath !== '/exercises' &&
      fsPath !== '\\exercises'
    ) {
      return fsPath;
    }
  }

  const defaultUri = vscode.Uri.file(path.join(os.homedir(), 'kubelings'));

  const selected = await vscode.window.showOpenDialog({
    canSelectFiles: false,
    canSelectFolders: true,
    canSelectMany: false,
    defaultUri,
    openLabel: 'Select Workspace Folder',
    title: 'Select Folder for Kubelings Exercises',
  });

  if (selected && selected.length > 0) {
    return selected[0].fsPath;
  }

  return path.join(os.homedir(), 'kubelings');
}

  // 2. kubelings.openExercise
  const openExerciseCmd = vscode.commands.registerCommand(
    'kubelings.openExercise',
    async (relPathOrItem?: ExerciseTreeItem | string, maybeName?: string) => {
      let relPath: string | undefined;
      let exName: string | undefined;

      if (typeof relPathOrItem === 'string') {
        relPath = relPathOrItem;
        exName = maybeName || path.basename(relPath).replace(/\.(yaml|yml|py)$/i, '');
      } else if (relPathOrItem instanceof ExerciseTreeItem) {
        relPath =
          relPathOrItem.fullPath && fs.existsSync(relPathOrItem.fullPath)
            ? relPathOrItem.fullPath
            : relPathOrItem.exercise.path;
        exName = relPathOrItem.exercise.name;
      } else if (
        relPathOrItem &&
        typeof relPathOrItem === 'object' &&
        'exercise' in relPathOrItem
      ) {
        const item = relPathOrItem as ExerciseTreeItem;
        relPath =
          item.fullPath && fs.existsSync(item.fullPath)
            ? item.fullPath
            : item.exercise?.path;
        exName = item.exercise?.name;
      }

      if (!relPath) {
        vscode.window.showWarningMessage('No exercise path specified to open.');
        return;
      }

      const hasOpenFolder = Boolean(
        vscode.workspace.workspaceFolders &&
          vscode.workspace.workspaceFolders.length > 0 &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '/' &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '\\' &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '/exercises' &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '\\exercises'
      );
      const workspaceRoot = cliBridge.getEffectiveWorkspaceRoot();
      let resolved = resolveExercisePath(relPath, workspaceRoot);

      if (!fs.existsSync(resolved)) {
        const choice = await vscode.window.showInformationMessage(
          'Exercise file was not found locally. Would you like to initialize the Kubelings exercise workspace?',
          'Initialize Exercises',
          'Cancel'
        );

        if (choice === 'Initialize Exercises') {
          let targetDir = workspaceRoot;
          let shouldOpenFolder = false;

          if (!hasOpenFolder) {
            const selectedDir = await getOrSelectWorkspaceFolder();
            if (!selectedDir) {
              return;
            }
            targetDir = selectedDir;
            shouldOpenFolder = true;
          }

          try {
            await cliBridge.init(targetDir);
            vscode.window.showInformationMessage(
              'Kubelings exercises initialized successfully! 🎉'
            );
            resolved = resolveExercisePath(relPath, targetDir);
            if (shouldOpenFolder) {
              await vscode.commands.executeCommand(
                'vscode.openFolder',
                vscode.Uri.file(targetDir)
              );
              return;
            }
            treeDataProvider.refresh();
            statusBar.refresh().catch(() => {});
          } catch (e: unknown) {
            const message = e instanceof Error ? e.message : String(e);
            if (
              message.includes('already exists and is not empty') ||
              message.includes('Use --force')
            ) {
              vscode.window.showInformationMessage(
                `Kubelings exercises are already initialized in: ${targetDir}`
              );
              if (shouldOpenFolder) {
                await vscode.commands.executeCommand(
                  'vscode.openFolder',
                  vscode.Uri.file(targetDir)
                );
                return;
              }
              treeDataProvider.refresh();
              statusBar.refresh().catch(() => {});
              resolved = resolveExercisePath(relPath, targetDir);
            } else {
              vscode.window.showErrorMessage(
                `Failed to initialize exercises: ${message}`
              );
              return;
            }
          }
        } else {
          return;
        }
      }

      if (fs.existsSync(resolved)) {
        try {
          const doc = await vscode.workspace.openTextDocument(
            vscode.Uri.file(resolved)
          );
          await vscode.window.showTextDocument(doc);
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : String(err);
          vscode.window.showErrorMessage(
            `Failed to open exercise file: ${message}`
          );
        }
      } else {
        vscode.window.showErrorMessage(
          `Exercise file still not found at: ${resolved}`
        );
      }
    }
  );
  context.subscriptions.push(openExerciseCmd);

  // 3. kubelings.initExercises
  const initExercisesCmd = vscode.commands.registerCommand(
    'kubelings.initExercises',
    async () => {
      const hasOpenFolder = Boolean(
        vscode.workspace.workspaceFolders &&
          vscode.workspace.workspaceFolders.length > 0 &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '/' &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '\\' &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '/exercises' &&
          vscode.workspace.workspaceFolders[0].uri.fsPath !== '\\exercises'
      );
      let targetDir = cliBridge.getEffectiveWorkspaceRoot();
      let shouldOpenFolder = false;

      if (!hasOpenFolder) {
        const selectedDir = await getOrSelectWorkspaceFolder();
        if (!selectedDir) {
          return;
        }
        targetDir = selectedDir;
        shouldOpenFolder = true;
      }

      try {
        await cliBridge.init(targetDir);
        vscode.window.showInformationMessage(
          'Kubelings exercises initialized successfully! 🎉'
        );
        if (shouldOpenFolder) {
          await vscode.commands.executeCommand(
            'vscode.openFolder',
            vscode.Uri.file(targetDir)
          );
          return;
        }
        treeDataProvider.refresh();
        statusBar.refresh().catch(() => {});
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        if (
          message.includes('already exists and is not empty') ||
          message.includes('Use --force')
        ) {
          const choice = await vscode.window.showWarningMessage(
            `Exercises already exist in ${targetDir}. Would you like to keep them or overwrite with fresh starter files?`,
            'Keep Existing',
            'Overwrite (Force)'
          );
          if (choice === 'Overwrite (Force)') {
            try {
              await cliBridge.init(targetDir, true);
              vscode.window.showInformationMessage(
                'Kubelings exercises re-initialized with fresh starter files! 🎉'
              );
              if (shouldOpenFolder) {
                await vscode.commands.executeCommand(
                  'vscode.openFolder',
                  vscode.Uri.file(targetDir)
                );
                return;
              }
              treeDataProvider.refresh();
              statusBar.refresh().catch(() => {});
            } catch (forceErr: unknown) {
              const forceMsg =
                forceErr instanceof Error ? forceErr.message : String(forceErr);
              vscode.window.showErrorMessage(
                `Failed to overwrite exercises: ${forceMsg}`
              );
            }
          } else if (choice === 'Keep Existing' && shouldOpenFolder) {
            await vscode.commands.executeCommand(
              'vscode.openFolder',
              vscode.Uri.file(targetDir)
            );
          }
        } else {
          vscode.window.showErrorMessage(
            `Failed to initialize exercises: ${message}`
          );
        }
      }
    }
  );
  context.subscriptions.push(initExercisesCmd);

  // 4. kubelings.runExercise
  const runExerciseCmd = vscode.commands.registerCommand(
    'kubelings.runExercise',
    async (arg?: ExerciseTreeItem | string | vscode.Uri) => {
      const exerciseName = resolveExerciseName(arg);
      if (!exerciseName) {
        vscode.window.showWarningMessage(
          'No active Kubelings exercise found. Please open an exercise file or select one in the Curriculum view.'
        );
        return;
      }

      try {
        const runResult = await cliBridge.run(exerciseName);
        treeDataProvider.refresh();
        statusBar.refresh().catch(() => {});

        if (runResult.passed) {
          vscode.window.showInformationMessage(
            `🎉 Exercise '${exerciseName}' passed! All verification checks succeeded.`
          );
        } else {
          const errMsg = runResult.error
            ? runResult.error.trim()
            : 'Evaluation checks failed.';
          vscode.window.showErrorMessage(
            `❌ Exercise '${exerciseName}' failed:\n${errMsg}`
          );
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        vscode.window.showErrorMessage(
          `Failed to evaluate exercise '${exerciseName}': ${message}`
        );
      }
    }
  );
  context.subscriptions.push(runExerciseCmd);

  // 5. kubelings.nextExercise
  const nextExerciseCmd = vscode.commands.registerCommand(
    'kubelings.nextExercise',
    async () => {
      try {
        const verifyRes = await cliBridge.verify();
        statusBar.update(verifyRes);
        treeDataProvider.refresh();

        if (!verifyRes.next_exercise) {
          vscode.window.showInformationMessage(
            '🏆 All Kubelings exercises completed! Congratulations!'
          );
          return;
        }

        const nextName = verifyRes.next_exercise;
        const workspaceRoot = cliBridge.getEffectiveWorkspaceRoot();

        // Locate exercise path
        let exerciseRelPath: string | undefined;
        const matchedItem = verifyRes.results.find((r) => r.name === nextName);
        if (matchedItem?.path) {
          exerciseRelPath = matchedItem.path;
        } else {
          const cachedExercise = treeDataProvider.findExercise(nextName);
          if (cachedExercise?.path) {
            exerciseRelPath = cachedExercise.path;
          } else {
            const listRes = await cliBridge.list();
            for (const ch of listRes.chapters) {
              const found = ch.exercises.find((ex) => ex.name === nextName);
              if (found) {
                exerciseRelPath = found.path;
                break;
              }
            }
          }
        }

        if (!exerciseRelPath) {
          vscode.window.showErrorMessage(
            `Could not locate file path for exercise '${nextName}'.`
          );
          return;
        }

        const fullPath = resolveExercisePath(exerciseRelPath, workspaceRoot);

        if (!fs.existsSync(fullPath)) {
          vscode.window.showErrorMessage(
            `Exercise file not found on disk at: ${fullPath}`
          );
          return;
        }

        const doc = await vscode.workspace.openTextDocument(
          vscode.Uri.file(fullPath)
        );
        await vscode.window.showTextDocument(doc);
        vscode.window.showInformationMessage(
          `Opened next exercise: ${nextName}`
        );
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        vscode.window.showErrorMessage(
          `Failed to navigate to next exercise: ${message}`
        );
      }
    }
  );
  context.subscriptions.push(nextExerciseCmd);

  // 4. kubelings.showHint
  const showHintCmd = vscode.commands.registerCommand(
    'kubelings.showHint',
    async (arg?: ExerciseTreeItem | string | vscode.Uri) => {
      const exerciseName = resolveExerciseName(arg);
      if (!exerciseName) {
        vscode.window.showWarningMessage(
          'No active Kubelings exercise found. Open an exercise file to see hints.'
        );
        return;
      }

      async function showProgressiveHint(
        name: string,
        index: number = 0
      ): Promise<void> {
        try {
          const hintRes = await cliBridge.hint(name, index);
          const currentHintNum = hintRes.hint_index + 1;
          const totalHints = hintRes.total_hints;
          const hasMore = currentHintNum < totalHints;
          const actions = hasMore ? ['Next Hint'] : [];

          const choice = await vscode.window.showInformationMessage(
            `💡 Hint [${currentHintNum}/${totalHints}] for ${name}:\n\n${hintRes.hint}`,
            ...actions
          );

          if (choice === 'Next Hint') {
            await showProgressiveHint(name, currentHintNum);
          }
        } catch (err: unknown) {
          const message = err instanceof Error ? err.message : String(err);
          vscode.window.showErrorMessage(
            `Failed to retrieve hint for '${name}': ${message}`
          );
        }
      }

      await showProgressiveHint(exerciseName, 0);
    }
  );
  context.subscriptions.push(showHintCmd);

  // 5. kubelings.showSolutionDiff
  const showSolutionDiffCmd = vscode.commands.registerCommand(
    'kubelings.showSolutionDiff',
    async (arg?: ExerciseTreeItem | string | vscode.Uri) => {
      const exerciseName = resolveExerciseName(arg);
      if (!exerciseName) {
        vscode.window.showWarningMessage(
          'No active Kubelings exercise found to compare solution.'
        );
        return;
      }

      const workspaceRoot = cliBridge.getEffectiveWorkspaceRoot();
      let exerciseRelPath: string | undefined;
      let solutionRelPath: string | undefined;

      const cached = treeDataProvider.findExercise(exerciseName);
      if (cached) {
        exerciseRelPath = cached.path;
        solutionRelPath =
          cached.solution_path ||
          cached.path.replace(/^exercises[\\/]/, 'solutions/');
      } else {
        try {
          const listRes = await cliBridge.list();
          for (const ch of listRes.chapters) {
            const found = ch.exercises.find((ex) => ex.name === exerciseName);
            if (found) {
              exerciseRelPath = found.path;
              solutionRelPath =
                found.solution_path ||
                found.path.replace(/^exercises[\\/]/, 'solutions/');
              break;
            }
          }
        } catch {
          // fallback search
        }
      }

      if (!exerciseRelPath || !solutionRelPath) {
        vscode.window.showErrorMessage(
          `Could not determine paths for exercise '${exerciseName}'.`
        );
        return;
      }

      const fullExercisePath = resolveExercisePath(
        exerciseRelPath,
        workspaceRoot
      );
      const fullSolutionPath = resolveExercisePath(
        solutionRelPath,
        workspaceRoot
      );

      if (!fs.existsSync(fullSolutionPath)) {
        vscode.window.showWarningMessage(
          `Reference solution for '${exerciseName}' not found at: ${fullSolutionPath}`
        );
        return;
      }

      const exerciseUri = vscode.Uri.file(fullExercisePath);
      const solutionUri = vscode.Uri.file(fullSolutionPath);

      await vscode.commands.executeCommand(
        'vscode.diff',
        exerciseUri,
        solutionUri,
        `${exerciseName}: Exercise ↔ Reference Solution`
      );
    }
  );
  context.subscriptions.push(showSolutionDiffCmd);

  // kubelings.openSolution
  const openSolutionCmd = vscode.commands.registerCommand(
    'kubelings.openSolution',
    async (arg?: ExerciseTreeItem | string | vscode.Uri) => {
      const exerciseName = resolveExerciseName(arg);
      if (!exerciseName) {
        vscode.window.showWarningMessage(
          'No active Kubelings exercise found to open solution.'
        );
        return;
      }
      const workspaceRoot = cliBridge.getEffectiveWorkspaceRoot();
      let solutionRelPath: string | undefined;

      const cached = treeDataProvider.findExercise(exerciseName);
      if (cached) {
        solutionRelPath =
          cached.solution_path ||
          cached.path.replace(/^exercises[\\/]/, 'solutions/');
      } else {
        try {
          const listRes = await cliBridge.list();
          for (const ch of listRes.chapters) {
            const found = ch.exercises.find((ex) => ex.name === exerciseName);
            if (found) {
              solutionRelPath =
                found.solution_path ||
                found.path.replace(/^exercises[\\/]/, 'solutions/');
              break;
            }
          }
        } catch {
          // fallback search
        }
      }

      if (!solutionRelPath) {
        solutionRelPath = `solutions/${exerciseName}.yaml`;
      }

      const fullSolutionPath = resolveExercisePath(
        solutionRelPath,
        workspaceRoot
      );

      if (!fs.existsSync(fullSolutionPath)) {
        vscode.window.showWarningMessage(
          `Reference solution for '${exerciseName}' not found at: ${fullSolutionPath}`
        );
        return;
      }

      const doc = await vscode.workspace.openTextDocument(
        vscode.Uri.file(fullSolutionPath)
      );
      await vscode.window.showTextDocument(doc);
    }
  );
  context.subscriptions.push(openSolutionCmd);

  // kubelings.resetExercise
  const resetExerciseCmd = vscode.commands.registerCommand(
    'kubelings.resetExercise',
    async (arg?: ExerciseTreeItem | string | vscode.Uri) => {
      const exerciseName = resolveExerciseName(arg);
      if (!exerciseName) {
        vscode.window.showWarningMessage(
          'No active Kubelings exercise found to reset.'
        );
        return;
      }

      const choice = await vscode.window.showWarningMessage(
        `Are you sure you want to reset '${exerciseName}' back to its starter template? Any unsaved progress will be lost.`,
        'Reset Exercise',
        'Cancel'
      );

      if (choice !== 'Reset Exercise') {
        return;
      }

      try {
        await cliBridge.reset(exerciseName);
        vscode.window.showInformationMessage(
          `Exercise '${exerciseName}' reset to starter template.`
        );
        treeDataProvider.refresh();
        if (statusBar) {
          statusBar.refresh().catch(() => {});
        }

        const cached = treeDataProvider.findExercise(exerciseName);
        if (cached?.path) {
          const workspaceRoot = cliBridge.getEffectiveWorkspaceRoot();
          const fullPath = resolveExercisePath(cached.path, workspaceRoot);
          if (fs.existsSync(fullPath)) {
            const doc = await vscode.workspace.openTextDocument(
              vscode.Uri.file(fullPath)
            );
            await vscode.window.showTextDocument(doc);
          }
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        vscode.window.showErrorMessage(
          `Failed to reset exercise '${exerciseName}': ${message}`
        );
      }
    }
  );
  context.subscriptions.push(resetExerciseCmd);

  // 6. kubelings.startWatch
  const startWatchCmd = vscode.commands.registerCommand(
    'kubelings.startWatch',
    () => {
      let terminal = vscode.window.terminals.find(
        (t) => t.name === 'Kubelings Watch'
      );
      if (!terminal) {
        terminal = vscode.window.createTerminal('Kubelings Watch');
      }
      terminal.show();

      const resolved = cliBridge.resolveCommand();
      let commandStr = 'kubelings watch';
      if (resolved.command === 'uv') {
        commandStr = 'uv run kubelings watch';
      } else if (resolved.argsPrefix.includes('-m')) {
        commandStr = `"${resolved.command}" -m kubelings watch`;
      } else if (resolved.command !== 'kubelings') {
        commandStr = `"${resolved.command}" watch`;
      }

      terminal.sendText(commandStr);
    }
  );
  context.subscriptions.push(startWatchCmd);

  // 7. kubelings.checkCluster
  const checkClusterCmd = vscode.commands.registerCommand(
    'kubelings.checkCluster',
    async () => {
      try {
        const clusterRes = await cliBridge.cluster();
        if (clusterRes.available) {
          vscode.window.showInformationMessage(
            `✅ Kubernetes Cluster Connected!\nContext: ${clusterRes.context}\nProvider: ${clusterRes.provider}\nMode: ${clusterRes.cluster_mode}`
          );
        } else {
          vscode.window.showWarningMessage(
            `⚠️ No active Kubernetes cluster found.\nContext: ${clusterRes.context} (Mode: ${clusterRes.cluster_mode})\nLocal/offline validation exercises will still work!`
          );
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        vscode.window.showErrorMessage(
          `Failed to check Kubernetes cluster connection: ${message}`
        );
      }
    }
  );
  context.subscriptions.push(checkClusterCmd);

  // 8. kubelings.testAll
  const testAllCmd = vscode.commands.registerCommand(
    'kubelings.testAll',
    () => {
      let terminal = vscode.window.terminals.find(
        (t) => t.name === 'Kubelings Test'
      );
      if (!terminal) {
        terminal = vscode.window.createTerminal('Kubelings Test');
      }
      terminal.show();

      const resolved = cliBridge.resolveCommand();
      let commandStr = 'kubelings test';
      if (resolved.command === 'uv') {
        commandStr = 'uv run kubelings test';
      } else if (resolved.argsPrefix.includes('-m')) {
        commandStr = `"${resolved.command}" -m kubelings test`;
      } else if (resolved.command !== 'kubelings') {
        commandStr = `"${resolved.command}" test`;
      }

      terminal.sendText(commandStr);
    }
  );
  context.subscriptions.push(testAllCmd);

  // 9. kubelings.openWalkthrough
  const openWalkthroughCmd = vscode.commands.registerCommand(
    'kubelings.openWalkthrough',
    async (stepId?: string) => {
      const target = stepId
        ? `dnf0.kubelings-vscode#kubelings.walkthrough#${stepId}`
        : 'dnf0.kubelings-vscode#kubelings.walkthrough';
      await vscode.commands.executeCommand(
        'workbench.action.openWalkthrough',
        target,
        false
      );
    }
  );
  context.subscriptions.push(openWalkthroughCmd);
}
