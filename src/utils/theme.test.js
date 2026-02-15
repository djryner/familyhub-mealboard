import { test } from 'node:test';
import assert from 'node:assert';
import { getTheme } from './theme.js';

test('getTheme returns "valentines" for February', () => {
  const date = new Date('2023-02-15');
  assert.strictEqual(getTheme(date), 'valentines');
});

test('getTheme returns "thanksgiving" for November', () => {
  const date = new Date('2023-11-24');
  assert.strictEqual(getTheme(date), 'thanksgiving');
});

test('getTheme returns "christmas" for December', () => {
  const date = new Date('2023-12-25');
  assert.strictEqual(getTheme(date), 'christmas');
});

test('getTheme returns "default" for other months', () => {
  const janDate = new Date('2023-01-01');
  assert.strictEqual(getTheme(janDate), 'default');

  const julDate = new Date('2023-07-04');
  assert.strictEqual(getTheme(julDate), 'default');
});
