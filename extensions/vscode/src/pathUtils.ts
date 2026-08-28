import * as fs from 'fs';
import * as os from 'os';
import * as path from 'path';

/**
 * Returns the effective workspace root, preventing read-only root ('/') crashes
 * when VS Code is opened without an active workspace folder.
 */
export function getEffectiveWorkspaceRoot(
  explicitRoot?: string,
  repoName: string = 'kubelings'
): string {
  // 1. If an explicit root was passed and is non-empty
  if (explicitRoot && explicitRoot.trim().length > 0) {
    return explicitRoot;
  }

  // 2. If VS Code has an open folder, use it
  try {
    const vsc = require('vscode');
    if (
      vsc?.workspace?.workspaceFolders &&
      vsc.workspace.workspaceFolders.length > 0
    ) {
      const fsPath = vsc.workspace.workspaceFolders[0]?.uri?.fsPath;
      if (fsPath && typeof fsPath === 'string' && fsPath.trim().length > 0) {
        return fsPath;
      }
    }
  } catch {
    // vscode module not available
  }

  // 3. If process.cwd() is valid and NOT root ('/' or '\')
  const cwd = process.cwd();
  if (
    cwd &&
    cwd !== '/' &&
    cwd !== '\\' &&
    fs.existsSync(cwd) &&
    (fs.existsSync(path.join(cwd, 'exercises')) ||
      fs.existsSync(path.join(cwd, 'pyproject.toml')) ||
      cwd.toLowerCase().includes(repoName.toLowerCase()))
  ) {
    return cwd;
  }

  // 4. Check standard candidate directories (e.g. ~/repos/kubelings, ~/kubelings, ~/Developer/kubelings)
  const home = os.homedir();
  const candidates = [
    path.join(home, 'repos', repoName),
    path.join(home, repoName),
    path.join(home, 'Developer', repoName),
    path.join(home, 'Documents', repoName),
    path.join(home, 'src', repoName),
  ];

  for (const candidate of candidates) {
    try {
      if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) {
        return candidate;
      }
    } catch {
      // ignore
    }
  }

  // 5. If process.cwd() is not root '/', fallback to cwd
  if (cwd && cwd !== '/' && cwd !== '\\') {
    return cwd;
  }

  // 6. Fall back safely to user home directory (NEVER root '/')
  return home || (process.platform === 'win32' ? 'C:\\' : '/tmp');
}

/**
 * Robustly resolves an exercise relative path (e.g. "exercises/01_pods/pods01.py")
 * against the current workspace, checking:
 * 1. Absolute paths that exist on disk
 * 2. Direct resolution against workspace root (e.g. workspaceRoot/exercises/01_pods/pods01.py)
 * 3. Stripping 'exercises/' prefix if workspace is already inside exercises/ (e.g. workspaceRoot/01_pods/pods01.py)
 * 4. Checking if workspace is inside an individual chapter directory (e.g. workspaceRoot/pods01.py)
 * 5. Ascending parent directory traversal up to 8 levels (both full path and stripped path)
 * 6. Fallback to direct resolution against workspace root
 */
export function resolveExercisePath(
  exPath: string,
  workspaceRoot?: string
): string {
  const root = getEffectiveWorkspaceRoot(workspaceRoot);

  // 1. If path is already absolute and exists on disk
  if (path.isAbsolute(exPath) && fs.existsSync(exPath)) {
    return exPath;
  }

  // 2. Direct resolve with workspaceRoot (e.g. workspaceRoot/exercises/01_pods/pods01.py)
  const directPath = path.resolve(root, exPath);
  if (fs.existsSync(directPath)) {
    return directPath;
  }

  // 3. If workspaceRoot is itself inside 'exercises' or ends with 'exercises', strip leading 'exercises/'
  const isExercisesPrefix =
    exPath.startsWith('exercises/') || exPath.startsWith('exercises\\');
  if (isExercisesPrefix) {
    const stripped = exPath.replace(/^exercises[/\\]/, '');
    const strippedPath = path.resolve(root, stripped);
    if (fs.existsSync(strippedPath)) {
      return strippedPath;
    }

    // 4. If workspace is inside an individual chapter directory (e.g. 01_pods), check basename
    const filenameOnly = path.basename(exPath);
    const directFile = path.resolve(root, filenameOnly);
    if (fs.existsSync(directFile)) {
      return directFile;
    }
  }

  // Also check solutions/ prefix stripping if resolving solution paths
  const isSolutionsPrefix =
    exPath.startsWith('solutions/') || exPath.startsWith('solutions\\');
  if (isSolutionsPrefix) {
    const stripped = exPath.replace(/^solutions[/\\]/, '');
    const strippedPath = path.resolve(root, stripped);
    if (fs.existsSync(strippedPath)) {
      return strippedPath;
    }

    const filenameOnly = path.basename(exPath);
    const directFile = path.resolve(root, filenameOnly);
    if (fs.existsSync(directFile)) {
      return directFile;
    }
  }

  // 5. If workspaceRoot is in a subfolder of a repo, search parent directories up to 8 levels
  let cur = root;
  for (let i = 0; i < 8; i++) {
    const candidateFull = path.resolve(cur, exPath);
    if (fs.existsSync(candidateFull)) {
      return candidateFull;
    }

    if (isExercisesPrefix) {
      const stripped = exPath.replace(/^exercises[/\\]/, '');
      const candidateStripped = path.resolve(cur, stripped);
      if (fs.existsSync(candidateStripped)) {
        return candidateStripped;
      }
    }

    if (isSolutionsPrefix) {
      const stripped = exPath.replace(/^solutions[/\\]/, '');
      const candidateStripped = path.resolve(cur, stripped);
      if (fs.existsSync(candidateStripped)) {
        return candidateStripped;
      }
    }

    const parent = path.dirname(cur);
    if (parent === cur) {
      break;
    }
    cur = parent;
  }

  // 6. Default fallback to direct resolution
  return directPath;
}
