import './vscodeMock';
import * as assert from 'node:assert';
import { describe, it } from 'node:test';
import * as vscode from 'vscode';
import { KubelingsCliBridge } from '../src/cliBridge';
import {
  KubelingsCodeActionProvider,
  KubelingsDiagnosticsProvider,
} from '../src/diagnostics';
import { CliRunResponse } from '../src/types';

describe('Kubelings Diagnostics - KubelingsDiagnosticsProvider', () => {
  class MockBridgeSuccess extends KubelingsCliBridge {
    public async run(name: string): Promise<CliRunResponse> {
      return {
        exercise: name,
        passed: true,
        has_not_done_marker: false,
      };
    }
  }

  class MockBridgeFailureMarker extends KubelingsCliBridge {
    public async run(name: string): Promise<CliRunResponse> {
      return {
        exercise: name,
        passed: false,
        has_not_done_marker: true,
        error: "AssertionError: Pod name must be 'nginx-web'",
      };
    }
  }

  class MockBridgeFailureErrorLine extends KubelingsCliBridge {
    public async run(name: string): Promise<CliRunResponse> {
      return {
        exercise: name,
        passed: false,
        has_not_done_marker: false,
        error: 'SyntaxError: invalid syntax',
        error_line: 5,
      };
    }
  }

  it('ignores non-exercise files during save', async () => {
    const bridge = new MockBridgeSuccess();
    const provider = new KubelingsDiagnosticsProvider(bridge);

    const doc: any = {
      uri: vscode.Uri.file('/workspace/src/app.ts'),
      fileName: '/workspace/src/app.ts',
      getText: () => 'console.log("hello");',
    };

    const res = await provider.handleDocumentSave(doc);
    assert.strictEqual(res, undefined);
  });

  it('clears diagnostics when exercise passes', async () => {
    const bridge = new MockBridgeSuccess();
    const provider = new KubelingsDiagnosticsProvider(bridge);

    const uri = vscode.Uri.file('/workspace/exercises/01_pods/pods01.py');
    const doc: any = {
      uri,
      fileName: '/workspace/exercises/01_pods/pods01.py',
      getText: () => 'def verify(): pass',
    };

    // Pre-populate diagnostic
    const initialDiag = new vscode.Diagnostic(
      new vscode.Range(
        new vscode.Position(0, 0),
        new vscode.Position(0, 10)
      ),
      'old error'
    );
    provider.getDiagnosticCollection().set(uri, [initialDiag]);
    assert.strictEqual(
      provider.getDiagnosticCollection().get(uri)?.length,
      1
    );

    const res = await provider.handleDocumentSave(doc);
    assert.ok(res?.passed);
    assert.strictEqual(
      provider.getDiagnosticCollection().get(uri),
      undefined
    );
  });

  it('generates diagnostic at # I AM NOT DONE line with Warning severity', async () => {
    const bridge = new MockBridgeFailureMarker();
    const provider = new KubelingsDiagnosticsProvider(bridge);

    const uri = vscode.Uri.file('/workspace/exercises/01_pods/pods01.py');
    const docContent = [
      '# Exercise 1',
      '# I AM NOT DONE',
      'manifest = {"kind": "Pod"}',
    ].join('\n');

    const doc: any = {
      uri,
      fileName: '/workspace/exercises/01_pods/pods01.py',
      getText: () => docContent,
    };

    const res = await provider.handleDocumentSave(doc);
    assert.strictEqual(res?.passed, false);

    const diagnostics = provider.getDiagnosticCollection().get(uri);
    assert.ok(diagnostics && diagnostics.length === 1);
    const diag = diagnostics[0];
    assert.strictEqual(diag.range.start.line, 1);
    assert.strictEqual(
      diag.severity,
      vscode.DiagnosticSeverity.Warning
    );
    assert.strictEqual(diag.source, 'kubelings');
    assert.strictEqual(diag.code, 'pods01');
    assert.ok(diag.message.includes('AssertionError'));
  });

  it('generates diagnostic at specific error line when no marker present', async () => {
    const bridge = new MockBridgeFailureErrorLine();
    const provider = new KubelingsDiagnosticsProvider(bridge);

    const uri = vscode.Uri.file('/workspace/exercises/01_pods/pods01.py');
    const docContent = [
      'line 1',
      'line 2',
      'line 3',
      'line 4',
      'line 5 with syntax error',
      'line 6',
    ].join('\n');

    const doc: any = {
      uri,
      fileName: '/workspace/exercises/01_pods/pods01.py',
      getText: () => docContent,
    };

    const res = await provider.handleDocumentSave(doc);
    assert.strictEqual(res?.passed, false);

    const diagnostics = provider.getDiagnosticCollection().get(uri);
    assert.ok(diagnostics && diagnostics.length === 1);
    const diag = diagnostics[0];
    // error_line 5 in 1-indexed becomes line index 4
    assert.strictEqual(diag.range.start.line, 4);
    assert.strictEqual(diag.severity, vscode.DiagnosticSeverity.Error);
    assert.ok(diag.message.includes('SyntaxError'));
  });
});

describe('Kubelings Code Actions - KubelingsCodeActionProvider', () => {
  it('returns empty actions if no kubelings diagnostics on document', () => {
    const provider = new KubelingsCodeActionProvider();
    const doc: any = {
      uri: vscode.Uri.file('/workspace/exercises/01_pods/pods01.py'),
      fileName: '/workspace/exercises/01_pods/pods01.py',
    };
    const range = new vscode.Range(
      new vscode.Position(0, 0),
      new vscode.Position(0, 0)
    );
    const context: any = {
      diagnostics: [
        {
          source: 'pylance',
          message: 'unused variable',
        },
      ],
    };

    const actions = provider.provideCodeActions(doc, range, context);
    assert.strictEqual(actions.length, 0);
  });

  it('provides Hint and Reference Solution code actions when kubelings diagnostics exist', () => {
    const provider = new KubelingsCodeActionProvider();
    const doc: any = {
      uri: vscode.Uri.file('/workspace/exercises/01_pods/pods01.py'),
      fileName: '/workspace/exercises/01_pods/pods01.py',
    };
    const range = new vscode.Range(
      new vscode.Position(1, 0),
      new vscode.Position(1, 15)
    );
    const diag = new vscode.Diagnostic(
      range,
      'Exercise not completed',
      vscode.DiagnosticSeverity.Warning
    );
    diag.source = 'kubelings';
    diag.code = 'pods01';

    const context: any = {
      diagnostics: [diag],
    };

    const actions = provider.provideCodeActions(doc, range, context);
    assert.strictEqual(actions.length, 2);

    const hintAction = actions.find((a) => a.title.includes('Reveal Hint'));
    assert.ok(hintAction);
    assert.strictEqual(hintAction?.command?.command, 'kubelings.showHint');
    assert.deepStrictEqual(hintAction?.command?.arguments, ['pods01']);
    assert.strictEqual(hintAction?.isPreferred, true);

    const diffAction = actions.find((a) =>
      a.title.includes('Compare with Reference Solution')
    );
    assert.ok(diffAction);
    assert.strictEqual(
      diffAction?.command?.command,
      'kubelings.showSolutionDiff'
    );
    assert.deepStrictEqual(diffAction?.command?.arguments, ['pods01']);
  });
});
