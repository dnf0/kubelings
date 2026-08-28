import { execFile } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import {
  CliClusterResponse,
  CliHintResponse,
  CliListResponse,
  CliRunResponse,
  CliTourResponse,
  CliVerifyResponse,
  ResolvedCommand,
} from './types';

export interface CliBridgeOptions {
  workspaceRoot?: string;
  customPythonPath?: string;
}

export class KubelingsCliBridge {
  private workspaceRoot?: string;
  private customPythonPath?: string;

  constructor(options?: CliBridgeOptions) {
    this.workspaceRoot = options?.workspaceRoot;
    this.customPythonPath = options?.customPythonPath;
  }

  /**
   * Retrieves the effective workspace directory.
   */
  public getEffectiveWorkspaceRoot(): string {
    if (this.workspaceRoot) {
      return this.workspaceRoot;
    }
    try {
      // Safely access vscode workspace if loaded in extension runtime
      const vscode = require('vscode');
      if (vscode?.workspace?.workspaceFolders?.length > 0) {
        return vscode.workspace.workspaceFolders[0].uri.fsPath;
      }
    } catch {
      // vscode not loaded (e.g. running outside extension host in tests)
    }
    return process.cwd();
  }

  /**
   * Retrieves custom python path from constructor or VS Code settings.
   */
  public getCustomPythonPath(): string {
    if (this.customPythonPath) {
      return this.customPythonPath;
    }
    try {
      const vscode = require('vscode');
      const configPath = vscode?.workspace?.getConfiguration('kubelings')?.get('pythonPath');
      if (typeof configPath === 'string' && configPath.trim().length > 0) {
        return configPath.trim();
      }
    } catch {
      // vscode not loaded
    }
    return '';
  }

  /**
   * Resolves the executable and prefix arguments based on environment and config.
   */
  public resolveCommand(workspaceRoot?: string): ResolvedCommand {
    const root = workspaceRoot || this.getEffectiveWorkspaceRoot();
    const customPath = this.getCustomPythonPath();

    if (customPath) {
      const isPython =
        customPath.endsWith('python') ||
        customPath.endsWith('python.exe') ||
        customPath.endsWith('python3') ||
        customPath.endsWith('python3.exe');
      if (isPython) {
        return { command: customPath, argsPrefix: ['-m', 'kubelings'] };
      }
      return { command: customPath, argsPrefix: [] };
    }

    // Check workspace .venv/bin/kubelings or .venv/Scripts/kubelings.exe
    const venvKubelingsPosix = path.join(root, '.venv', 'bin', 'kubelings');
    const venvKubelingsWin = path.join(root, '.venv', 'Scripts', 'kubelings.exe');
    if (fs.existsSync(venvKubelingsPosix)) {
      return { command: venvKubelingsPosix, argsPrefix: [] };
    }
    if (fs.existsSync(venvKubelingsWin)) {
      return { command: venvKubelingsWin, argsPrefix: [] };
    }

    // Check workspace .venv/bin/python or .venv/Scripts/python.exe
    const venvPythonPosix = path.join(root, '.venv', 'bin', 'python');
    const venvPythonWin = path.join(root, '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvPythonPosix)) {
      return { command: venvPythonPosix, argsPrefix: ['-m', 'kubelings'] };
    }
    if (fs.existsSync(venvPythonWin)) {
      return { command: venvPythonWin, argsPrefix: ['-m', 'kubelings'] };
    }

    // Check if pyproject.toml or uv.lock exists in root (indicating uv project)
    if (
      fs.existsSync(path.join(root, 'pyproject.toml')) ||
      fs.existsSync(path.join(root, 'uv.lock'))
    ) {
      return { command: 'uv', argsPrefix: ['run', 'kubelings'] };
    }

    // Fallback to globally available kubelings executable
    return { command: 'kubelings', argsPrefix: [] };
  }

  /**
   * Executes a kubelings CLI command and parses the returned JSON payload.
   */
  public async executeJson<T>(args: string[], cwd?: string): Promise<T> {
    const effectiveCwd = cwd || this.getEffectiveWorkspaceRoot();
    const resolved = this.resolveCommand(effectiveCwd);
    const fullArgs = args.includes('--json')
      ? [...resolved.argsPrefix, ...args]
      : [...resolved.argsPrefix, ...args, '--json'];

    return new Promise<T>((resolve, reject) => {
      execFile(
        resolved.command,
        fullArgs,
        {
          cwd: effectiveCwd,
          maxBuffer: 10 * 1024 * 1024,
          timeout: 60000,
          env: { ...process.env, PYTHONUNBUFFERED: '1' },
        },
        (error, stdout, stderr) => {
          const rawOutput = (stdout || '').trim();
          if (rawOutput) {
            try {
              // Extract JSON substring if surrounding output contains banners
              const jsonStart = rawOutput.indexOf('{');
              const jsonEnd = rawOutput.lastIndexOf('}');
              if (jsonStart !== -1 && jsonEnd !== -1 && jsonEnd >= jsonStart) {
                const jsonStr = rawOutput.substring(jsonStart, jsonEnd + 1);
                const parsed = JSON.parse(jsonStr) as T;
                return resolve(parsed);
              }
              const parsed = JSON.parse(rawOutput) as T;
              return resolve(parsed);
            } catch (parseError) {
              if (error) {
                return reject(
                  new Error(
                    `Command '${resolved.command} ${fullArgs.join(' ')}' failed with code ${error.code}: ${stderr || error.message}`
                  )
                );
              }
              return reject(
                new Error(
                  `Failed to parse JSON output from '${resolved.command} ${fullArgs.join(' ')}': ${parseError instanceof Error ? parseError.message : String(parseError)}\nRaw output: ${rawOutput}`
                )
              );
            }
          }

          if (error) {
            return reject(
              new Error(
                `Command '${resolved.command} ${fullArgs.join(' ')}' failed with code ${error.code}: ${stderr || error.message}`
              )
            );
          }

          return reject(
            new Error(
              `Command '${resolved.command} ${fullArgs.join(' ')}' returned empty output`
            )
          );
        }
      );
    });
  }

  /**
   * Retrieves the full curriculum tree and exercise metadata.
   */
  public async list(cwd?: string): Promise<CliListResponse> {
    return this.executeJson<CliListResponse>(['list'], cwd);
  }

  /**
   * Executes evaluation of a single exercise.
   */
  public async run(exerciseName: string, cwd?: string): Promise<CliRunResponse> {
    return this.executeJson<CliRunResponse>(['run', exerciseName], cwd);
  }

  /**
   * Evaluates all curriculum exercises and aggregates workspace completion progress.
   */
  public async verify(cwd?: string): Promise<CliVerifyResponse> {
    return this.executeJson<CliVerifyResponse>(['verify'], cwd);
  }

  /**
   * Checks connectivity to the local or remote Kubernetes cluster.
   */
  public async cluster(cwd?: string): Promise<CliClusterResponse> {
    return this.executeJson<CliClusterResponse>(['cluster'], cwd);
  }

  /**
   * Fetches progressive hints for a specified exercise.
   */
  public async hint(
    exerciseName: string,
    index?: number,
    cwd?: string
  ): Promise<CliHintResponse> {
    const args = ['hint', exerciseName];
    if (index !== undefined) {
      args.push('--index', String(index));
    }
    return this.executeJson<CliHintResponse>(args, cwd);
  }

  /**
   * Retrieves the 5-step onboarding tour curriculum and metadata.
   */
  public async tour(step?: number, cwd?: string): Promise<CliTourResponse> {
    const args = ['tour'];
    if (step !== undefined) {
      args.push('--step', String(step));
    }
    return this.executeJson<CliTourResponse>(args, cwd);
  }

  /**
   * Initializes or scaffolds curriculum exercises into the target workspace.
   */
  public async init(
    targetDir?: string
  ): Promise<{ success: boolean; message: string }> {
    const cwd = targetDir || this.getEffectiveWorkspaceRoot();
    const resolved = this.resolveCommand(cwd);
    const args = targetDir
      ? [...resolved.argsPrefix, 'init', '--dir', targetDir]
      : [...resolved.argsPrefix, 'init'];

    return new Promise<{ success: boolean; message: string }>((resolve, reject) => {
      execFile(
        resolved.command,
        args,
        {
          cwd,
          maxBuffer: 5 * 1024 * 1024,
          timeout: 30000,
          env: { ...process.env, PYTHONUNBUFFERED: '1' },
        },
        (error, stdout, stderr) => {
          if (error && error.code !== 0) {
            return reject(
              new Error(
                stderr?.trim() ||
                  stdout?.trim() ||
                  `Command failed with code ${error.code}`
              )
            );
          }
          resolve({
            success: true,
            message: stdout?.trim() || 'Initialized exercises successfully.',
          });
        }
      );
    });
  }
}

