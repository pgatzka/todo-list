import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  { ignores: ['**/dist', '**/coverage', '**/node_modules'] },
  // Rules every workspace shares. Environment globals are deliberately absent:
  // a browser bundle and a Node process do not have the same ones, so each
  // workspace declares its own below.
  {
    extends: [js.configs.recommended, ...tseslint.configs.strictTypeChecked],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      // CLAUDE.md forbids `any` outright: use `unknown` and narrow, or model the
      // type properly. These are errors rather than warnings so CI enforces it.
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/no-unsafe-assignment': 'error',

      // Unused values are dead code. The underscore prefix is the documented
      // escape hatch for a deliberately ignored parameter.
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
    },
  },
  // The frontend runs in the browser and is the only workspace with React in it.
  {
    files: ['packages/web/**/*.{ts,tsx}'],
    languageOptions: { globals: globals.browser },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    },
  },
  // Test files legitimately do things the strict rules flag: asserting on
  // promises, building deliberately malformed input, and reaching for non-null
  // assertions on values a test has just created.
  {
    files: ['**/*.test.{ts,tsx}', 'packages/web/src/setupTests.ts'],
    languageOptions: { globals: { ...globals.browser, ...globals.node } },
    rules: {
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/unbound-method': 'off',
    },
  },
  // Config files run in Node, not the browser.
  {
    files: ['**/*.config.{ts,js}'],
    languageOptions: { globals: globals.node },
  },
  prettier,
);
