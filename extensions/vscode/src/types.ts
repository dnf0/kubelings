/**
 * Type definitions matching the Kubelings Python CLI JSON API models.
 */

export type ExerciseStatus = 'completed' | 'in_progress' | 'not_started';

export interface CliExercise {
  name: string;
  title: string;
  path: string;
  solution_path?: string;
  chapter_name: string;
  requires_cluster: boolean;
  has_not_done?: boolean;
  hints?: string[];
}

export interface CliChapter {
  number: number;
  name: string;
  title: string;
  description: string;
  exercises: CliExercise[];
}

export interface CliListResponse {
  total_chapters: number;
  total_exercises: number;
  chapters: CliChapter[];
}

export interface CliRunResponse {
  exercise: string;
  passed: boolean;
  has_not_done_marker: boolean;
  exit_code?: number;
  output?: string;
  error?: string | null;
  error_line?: number | null;
  duration_ms?: number;
  hints_available?: number;
}

export interface CliVerifyItem {
  name: string;
  title: string;
  path: string;
  chapter: string;
  status: ExerciseStatus;
  passed: boolean;
  has_not_done_marker: boolean;
  duration_ms: number;
}

export interface CliVerifyResponse {
  total: number;
  completed: number;
  in_progress: number;
  not_started: number;
  percentage: number;
  next_exercise: string | null;
  results: CliVerifyItem[];
}

export interface CliClusterResponse {
  available: boolean;
  context: string;
  provider: string;
  cluster_mode: 'live' | 'offline' | string;
}

export interface CliHintResponse {
  exercise: string;
  hint_index: number;
  total_hints: number;
  hint: string;
  error?: string;
}

export interface CliTourStep {
  step: number;
  step_num: number;
  name: string;
  title: string;
  description: string;
}

export interface CliTourResponse {
  total_steps: number;
  steps: CliTourStep[];
}

export interface ResolvedCommand {
  command: string;
  argsPrefix: string[];
}
