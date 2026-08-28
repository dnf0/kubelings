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
  const isInvalidRoot = (p?: string): boolean => {
    if (!p || typeof p !== 'string') {
      return true;
    }
    const trimmed = p.trim();
    return (
      trimmed.length === 0 ||
      trimmed === '/' ||
      trimmed === '\\' ||
      trimmed === '/exercises' ||
      trimmed === '\\exercises'
    );
  };

  // 1. If an explicit root was passed and is valid
  if (!isInvalidRoot(explicitRoot)) {
    return explicitRoot!;
  }

  // 2. If VS Code has an open folder, use it if not root
  try {
    const vsc = require('vscode');
    if (
      vsc?.workspace?.workspaceFolders &&
      vsc.workspace.workspaceFolders.length > 0
    ) {
      const fsPath = vsc.workspace.workspaceFolders[0]?.uri?.fsPath;
      if (!isInvalidRoot(fsPath)) {
        return fsPath;
      }
    }
  } catch {
    // vscode module not available
  }

  // 3. If process.cwd() is valid and NOT root ('/' or '\')
  const cwd = process.cwd();
  if (
    !isInvalidRoot(cwd) &&
    fs.existsSync(cwd) &&
    (fs.existsSync(path.join(cwd, 'exercises')) ||
      fs.existsSync(path.join(cwd, 'pyproject.toml')) ||
      cwd.toLowerCase().includes(repoName.toLowerCase()))
  ) {
    return cwd;
  }

  // 4. Check standard candidate directories (e.g. ~/kubelings, ~/repos/kubelings, ~/Developer/kubelings)
  const home = os.homedir();
  const candidates = [
    path.join(home, repoName),
    path.join(home, 'repos', repoName),
    path.join(home, 'Developer', repoName),
    path.join(home, 'Documents', repoName),
    path.join(home, 'src', repoName),
  ];

  for (const candidate of candidates) {
    try {
      if (
        fs.existsSync(candidate) &&
        (fs.existsSync(path.join(candidate, 'exercises')) ||
          fs.statSync(candidate).isDirectory())
      ) {
        return candidate;
      }
    } catch {
      // ignore
    }
  }

  // 5. If process.cwd() is not root '/', fallback to cwd
  if (!isInvalidRoot(cwd) && fs.existsSync(cwd)) {
    return cwd;
  }

  // 6. Fall back safely to ~/kubelings (NEVER root '/')
  return path.join(home, repoName);
}

/**
 * Returns a list of candidate file paths for a given target path, prioritizing
 * .yaml, then .yml, then .py extensions.
 */
export function getCandidateFilePaths(targetPath: string): string[] {
  if (!targetPath || typeof targetPath !== 'string') {
    return [];
  }
  const ext = path.extname(targetPath).toLowerCase();
  const basePath =
    ext === '.yaml' || ext === '.yml' || ext === '.py'
      ? targetPath.slice(0, -ext.length)
      : targetPath;

  const extensions =
    ext === '.yml'
      ? ['.yml', '.yaml', '.py']
      : ['.yaml', '.yml', '.py'];

  const candidates: string[] = [];
  for (const candidateExt of extensions) {
    const candidate = basePath + candidateExt;
    if (!candidates.includes(candidate)) {
      candidates.push(candidate);
    }
  }

  if (!candidates.includes(targetPath)) {
    candidates.push(targetPath);
  }
  if (!candidates.includes(basePath)) {
    candidates.push(basePath);
  }

  return candidates;
}

/**
 * Searches for an existing candidate file path on disk, checking .yaml, .yml, and .py.
 */
export function findExistingCandidate(targetPath: string): string | undefined {
  if (!targetPath || typeof targetPath !== 'string') {
    return undefined;
  }
  const candidates = getCandidateFilePaths(targetPath);
  for (const cand of candidates) {
    if (fs.existsSync(cand)) {
      return cand;
    }
  }
  return undefined;
}

/**
 * Robustly resolves an exercise relative path (e.g. "exercises/01_pods/pods01.yaml")
 * against the current workspace, checking:
 * 1. Absolute paths that exist on disk (and candidate extensions)
 * 2. Direct resolution against workspace root (e.g. workspaceRoot/exercises/01_pods/pods01.yaml)
 * 3. Stripping 'exercises/' prefix if workspace is already inside exercises/ (e.g. workspaceRoot/01_pods/pods01.yaml)
 * 4. Checking if workspace is inside an individual chapter directory (e.g. workspaceRoot/pods01.yaml)
 * 5. Ascending parent directory traversal up to 8 levels (both full path and stripped path)
 * 6. Checking standard locations (~/kubelings, ~/repos/kubelings, etc.)
 * 7. Fallback to direct resolution against workspace root
 */
export function resolveExercisePath(
  exPath: string,
  workspaceRoot?: string
): string {
  if (!exPath || typeof exPath !== 'string') {
    return '';
  }

  // 1. If path is already an absolute path that exists on disk
  if (path.isAbsolute(exPath)) {
    const existing = findExistingCandidate(exPath);
    if (existing) {
      return existing;
    }
    if (fs.existsSync(exPath)) {
      return exPath;
    }
  }

  // Normalize path: strip leading slashes so it is treated as a relative path
  const cleanPath = exPath.replace(/^[/\\]+/, '');

  const isInvalidRoot = (p?: string): boolean => {
    if (!p || typeof p !== 'string') {
      return true;
    }
    const trimmed = p.trim();
    return (
      trimmed.length === 0 ||
      trimmed === '/' ||
      trimmed === '\\' ||
      trimmed === '/exercises' ||
      trimmed === '\\exercises'
    );
  };

  const isExplicit = !isInvalidRoot(workspaceRoot);
  const root = getEffectiveWorkspaceRoot(workspaceRoot);

  // 2. Direct resolve with workspaceRoot (e.g. workspaceRoot/exercises/01_pods/pods01.yaml)
  const directPath = path.resolve(root, cleanPath);
  const directFound = findExistingCandidate(directPath);
  if (directFound) {
    return directFound;
  }

  // 3. If cleanPath starts with 'exercises/' or 'solutions/', try stripping the prefix
  const isExercisesPrefix =
    cleanPath.startsWith('exercises/') || cleanPath.startsWith('exercises\\');
  const isSolutionsPrefix =
    cleanPath.startsWith('solutions/') || cleanPath.startsWith('solutions\\');

  if (isExercisesPrefix || isSolutionsPrefix) {
    const stripped = cleanPath.replace(/^(exercises|solutions)[/\\]/, '');
    const strippedPath = path.resolve(root, stripped);
    const strippedFound = findExistingCandidate(strippedPath);
    if (strippedFound) {
      return strippedFound;
    }

    // 4. If workspace is inside an individual chapter directory, check basename
    const filenameOnly = path.basename(cleanPath);
    const directFile = path.resolve(root, filenameOnly);
    const fileFound = findExistingCandidate(directFile);
    if (fileFound) {
      return fileFound;
    }
  }

  // 5. If workspaceRoot is in a subfolder, search parent directories up to 8 levels
  let cur = root;
  for (let i = 0; i < 8; i++) {
    const candidateFull = path.resolve(cur, cleanPath);
    const candidateFullFound = findExistingCandidate(candidateFull);
    if (candidateFullFound) {
      return candidateFullFound;
    }

    if (isExercisesPrefix || isSolutionsPrefix) {
      const stripped = cleanPath.replace(/^(exercises|solutions)[/\\]/, '');
      const candidateStripped = path.resolve(cur, stripped);
      const candidateStrippedFound = findExistingCandidate(candidateStripped);
      if (candidateStrippedFound) {
        return candidateStrippedFound;
      }
    }

    const parent = path.dirname(cur);
    if (parent === cur) {
      break;
    }
    cur = parent;
  }

  // 6. Check standard candidate directories (e.g. ~/kubelings, ~/repos/kubelings) when no explicit root
  if (!isExplicit) {
    const home = os.homedir();
    const standardDirs = [
      path.join(home, 'kubelings'),
      path.join(home, 'repos', 'kubelings'),
      path.join(home, 'Developer', 'kubelings'),
      path.join(home, 'Documents', 'kubelings'),
      path.join(home, 'src', 'kubelings'),
    ];
    for (const standardDir of standardDirs) {
      const candidate = path.resolve(standardDir, cleanPath);
      const foundCandidate = findExistingCandidate(candidate);
      if (foundCandidate) {
        return foundCandidate;
      }
      if (isExercisesPrefix || isSolutionsPrefix) {
        const stripped = cleanPath.replace(/^(exercises|solutions)[/\\]/, '');
        const strippedCand = path.resolve(standardDir, stripped);
        const foundStripped = findExistingCandidate(strippedCand);
        if (foundStripped) {
          return foundStripped;
        }
      }
      const candBase = path.resolve(standardDir, path.basename(cleanPath));
      const foundBase = findExistingCandidate(candBase);
      if (foundBase) {
        return foundBase;
      }
    }
  }

  // 7. Default fallback to direct resolution
  return directPath;
}
