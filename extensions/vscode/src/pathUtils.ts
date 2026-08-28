import * as fs from 'fs';
import * as path from 'path';

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
  let root: string;
  try {
    const vsc = require('vscode');
    root =
      workspaceRoot ||
      vsc?.workspace?.workspaceFolders?.[0]?.uri?.fsPath ||
      process.cwd();
  } catch {
    root = workspaceRoot || process.cwd();
  }

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
