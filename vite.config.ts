/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts'],
    css: false,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      // Entry points and type-only files carry no behaviour worth asserting on.
      exclude: ['src/main.tsx', 'src/vite-env.d.ts', 'src/setupTests.ts', '**/*.config.*'],
    },
  },
});
