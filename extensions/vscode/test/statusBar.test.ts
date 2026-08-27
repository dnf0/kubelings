import './vscodeMock';
import * as assert from 'node:assert';
import { describe, it } from 'node:test';
import { KubelingsCliBridge } from '../src/cliBridge';
import { KubelingsStatusBar } from '../src/statusBar';
import { CliVerifyResponse } from '../src/types';

describe('Kubelings Status Bar - KubelingsStatusBar', () => {
  const sampleVerifyData: CliVerifyResponse = {
    total: 10,
    completed: 4,
    in_progress: 1,
    not_started: 5,
    percentage: 40,
    next_exercise: 'pods05',
    results: [],
  };

  class MockVerifyBridge extends KubelingsCliBridge {
    public async verify(): Promise<CliVerifyResponse> {
      return sampleVerifyData;
    }
  }

  it('updates text and tooltip with verify metrics and next exercise', () => {
    const bridge = new MockVerifyBridge();
    const statusBar = new KubelingsStatusBar(bridge);

    statusBar.update(sampleVerifyData);
    const item = statusBar.getStatusBarItem();

    assert.ok(item.text.includes('4/10 (40%)'));
    assert.ok(item.text.includes('Next: pods05'));
    const tooltip = String(item.tooltip || '');
    assert.ok(tooltip.includes('4/10 Completed (40%)'));
    assert.strictEqual(item.command, 'kubelings.nextExercise');
    assert.strictEqual(
      statusBar.getLastVerifyData()?.next_exercise,
      'pods05'
    );
  });

  it('refreshes by calling cliBridge.verify()', async () => {
    const bridge = new MockVerifyBridge();
    const statusBar = new KubelingsStatusBar(bridge);

    const res = await statusBar.refresh();
    assert.ok(res);
    assert.strictEqual(res?.percentage, 40);
    assert.strictEqual(res?.next_exercise, 'pods05');
  });

  it('shows and hides status bar item correctly', () => {
    const bridge = new MockVerifyBridge();
    const statusBar = new KubelingsStatusBar(bridge);

    statusBar.show();
    const item: any = statusBar.getStatusBarItem();
    assert.strictEqual(item.visible, true);

    statusBar.hide();
    assert.strictEqual(item.visible, false);

    statusBar.dispose();
  });
});
