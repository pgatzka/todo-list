import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    // One glob per package: a new workspace is picked up without editing this,
    // and a package without tests is tolerated.
    projects: ['packages/*'],
    // Coverage is global in projects mode, so it is configured here rather than
    // in a package's own config, where it would be ignored.
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      // Entry points and type-only files carry no behaviour worth asserting on.
      exclude: [
        'packages/*/dist/**',
        'packages/web/src/main.tsx',
        'packages/web/src/vite-env.d.ts',
        'packages/web/src/setupTests.ts',
        '**/*.config.*',
      ],
    },
  },
});
