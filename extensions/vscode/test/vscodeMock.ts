import * as path from 'path';

export class TreeItem {
  public label?: string;
  public collapsibleState?: number;
  public description?: string | boolean;
  public tooltip?: string;
  public iconPath?: any;
  public command?: any;
  public contextValue?: string;

  constructor(label: string, collapsibleState?: number) {
    this.label = label;
    this.collapsibleState = collapsibleState ?? 0;
  }
}

export class ThemeIcon {
  constructor(public readonly id: string, public readonly color?: any) {}
}

export class ThemeColor {
  constructor(public readonly id: string) {}
}

export class Position {
  constructor(public readonly line: number, public readonly character: number) {}
}

export class Range {
  constructor(
    public readonly start: Position,
    public readonly end: Position
  ) {}
}

export class Diagnostic {
  public source?: string;
  public code?: string | number | { value: string | number; target: any };

  constructor(
    public readonly range: Range,
    public readonly message: string,
    public readonly severity: number = 0
  ) {}
}

export class CodeAction {
  public command?: any;
  public diagnostics?: Diagnostic[];
  public isPreferred?: boolean;

  constructor(public readonly title: string, public readonly kind?: any) {}
}

export class Uri {
  public scheme: string;
  public fsPath: string;
  public path: string;

  private constructor(scheme: string, fsPath: string, pathStr: string) {
    this.scheme = scheme;
    this.fsPath = fsPath;
    this.path = pathStr;
  }

  static file(filePath: string): Uri {
    return new Uri('file', filePath, filePath);
  }

  static parse(uriStr: string): Uri {
    return new Uri('file', uriStr, uriStr);
  }

  toString(): string {
    return `file://${this.fsPath}`;
  }
}

export class EventEmitter<T> {
  private listeners: ((e: T) => any)[] = [];

  get event() {
    return (listener: (e: T) => any) => {
      this.listeners.push(listener);
      return { dispose: () => {} };
    };
  }

  fire(data: T): void {
    for (const l of this.listeners) {
      l(data);
    }
  }

  dispose(): void {
    this.listeners = [];
  }
}

export class MockStatusBarItem {
  public alignment: number;
  public priority: number;
  public text: string = '';
  public tooltip: string = '';
  public command?: string;
  public visible: boolean = false;

  constructor(alignment: number, priority: number) {
    this.alignment = alignment;
    this.priority = priority;
  }

  show(): void {
    this.visible = true;
  }

  hide(): void {
    this.visible = false;
  }

  dispose(): void {
    this.visible = false;
  }
}

export class MockDiagnosticCollection {
  public readonly name: string;
  public entries: Map<string, Diagnostic[]> = new Map();

  constructor(name: string) {
    this.name = name;
  }

  set(uri: any, diagnostics: Diagnostic[]): void {
    const key = uri.toString ? uri.toString() : String(uri.fsPath || uri);
    this.entries.set(key, diagnostics);
  }

  get(uri: any): Diagnostic[] | undefined {
    const key = uri.toString ? uri.toString() : String(uri.fsPath || uri);
    return this.entries.get(key);
  }

  delete(uri: any): void {
    const key = uri.toString ? uri.toString() : String(uri.fsPath || uri);
    this.entries.delete(key);
  }

  clear(): void {
    this.entries.clear();
  }

  dispose(): void {
    this.clear();
  }
}

export interface MockTerminal {
  name: string;
  textSent: string[];
  shown: boolean;
  show(): void;
  sendText(text: string): void;
  dispose(): void;
}

export const mockVscode = {
  TreeItem,
  TreeItemCollapsibleState: {
    None: 0,
    Collapsed: 1,
    Expanded: 2,
  },
  ThemeIcon,
  ThemeColor,
  StatusBarAlignment: {
    Left: 1,
    Right: 2,
  },
  DiagnosticSeverity: {
    Error: 0,
    Warning: 1,
    Information: 2,
    Hint: 3,
  },
  Position,
  Range,
  Diagnostic,
  CodeActionKind: {
    QuickFix: 'quickfix',
  },
  CodeAction,
  Uri,
  EventEmitter,
  window: {
    createStatusBarItem: (alignment: number, priority: number) =>
      new MockStatusBarItem(alignment, priority),
    showInformationMessage: async (msg: string, ...items: string[]) => items[0],
    showErrorMessage: async (msg: string, ...items: string[]) => undefined,
    showWarningMessage: async (msg: string, ...items: string[]) => undefined,
    showTextDocument: async (doc: any) => ({ document: doc }),
    registerTreeDataProvider: (id: string, provider: any) => ({
      dispose: () => {},
    }),
    createTerminal: (name: string): MockTerminal => {
      const term: MockTerminal = {
        name,
        textSent: [],
        shown: false,
        show() {
          this.shown = true;
        },
        sendText(text: string) {
          this.textSent.push(text);
        },
        dispose() {},
      };
      mockVscode.window.terminals.push(term);
      return term;
    },
    terminals: [] as MockTerminal[],
    activeTextEditor: undefined as any,
  },
  workspace: {
    getConfiguration: (section?: string) => ({
      get: <T>(key: string, defaultValue?: T): T => defaultValue as T,
    }),
    openTextDocument: async (uriOrPath: any) => {
      const fsPath = typeof uriOrPath === 'string' ? uriOrPath : uriOrPath.fsPath;
      return {
        uri: typeof uriOrPath === 'string' ? Uri.file(uriOrPath) : uriOrPath,
        fileName: fsPath,
        getText: () => '',
      };
    },
    onDidSaveTextDocument: (cb: any) => ({ dispose: () => {} }),
    onDidChangeConfiguration: (cb: any) => ({ dispose: () => {} }),
    workspaceFolders: [] as any[],
  },
  languages: {
    createDiagnosticCollection: (name: string) =>
      new MockDiagnosticCollection(name),
    registerCodeActionsProvider: (selector: any, provider: any, meta?: any) => ({
      dispose: () => {},
    }),
  },
  commands: {
    registered: new Map<string, Function>(),
    registerCommand: (id: string, callback: Function) => {
      mockVscode.commands.registered.set(id, callback);
      return {
        dispose: () => {
          mockVscode.commands.registered.delete(id);
        },
      };
    },
    executeCommand: async (id: string, ...args: any[]) => {
      const handler = mockVscode.commands.registered.get(id);
      if (handler) {
        return handler(...args);
      }
      return undefined;
    },
  },
};

// Hook into Module prototype so 'vscode' can be required in test environment
const Module = require('module');
const originalRequire = Module.prototype.require;
Module.prototype.require = function (moduleName: string) {
  if (moduleName === 'vscode') {
    return mockVscode;
  }
  return originalRequire.apply(this, arguments);
};
