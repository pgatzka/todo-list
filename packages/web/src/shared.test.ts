import { readFileSync, readdirSync } from 'node:fs';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Todo } from '@todo/shared';

const sourceRoot = dirname(fileURLToPath(import.meta.url));
const packageRoot = resolve(sourceRoot, '..');

/** `from '…'`, `import('…')` and bare `import '…'`, which is all this repo writes. */
const importSpecifier = /(?:from|import)\s*\(?\s*['"]([^'"]+)['"]/g;

function importsEscapingThisPackage(): readonly string[] {
  const sources = readdirSync(sourceRoot, { recursive: true, encoding: 'utf8' }).filter((entry) =>
    /\.tsx?$/.test(entry),
  );

  return sources.flatMap((source) => {
    const file = resolve(sourceRoot, source);

    return [...readFileSync(file, 'utf8').matchAll(importSpecifier)]
      .map((match) => match[1] ?? '')
      .filter((specifier) => specifier.startsWith('.'))
      .filter((specifier) =>
        relative(packageRoot, resolve(dirname(file), specifier)).startsWith('..'),
      )
      .map((specifier) => `${source} -> ${specifier}`);
  });
}

// Structural: these assert how the web workspace reaches the shared package, not
// what the shared package contains. Superseded once the client actually consumes
// the API types (#34).
describe('@todo/shared from the web workspace', () => {
  // A compile-time assertion. Vitest strips the type import, so this test is
  // enforced by `npm run typecheck`, not by the test run.
  it('supplies the Todo type under its package name', () => {
    const todo: Todo = { id: '1', title: 'Buy milk', completed: false };

    expect(todo.completed).toBe(false);
  });

  // The counterpart that the type import cannot make: an erased import proves
  // nothing about the package's `exports` map or its built `dist`. The import is
  // dynamic because a types-only package has no value left to import statically.
  it('resolves at runtime through its package exports', async () => {
    await expect(import('@todo/shared')).resolves.toBeDefined();
  });

  it('is never reached by a relative path out of the workspace', () => {
    expect(importsEscapingThisPackage()).toEqual([]);
  });
});
