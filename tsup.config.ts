import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  outDir: 'dist',
  tsconfig: './tsconfig.build.json', // Use build-specific tsconfig
  platform: 'node', // Revert platform back to node
  sourcemap: true,
  clean: true,
  format: ['esm'], // Ensure you're targeting CommonJS
  dts: false, // Skip DTS generation to avoid external import issues // Ensure you're targeting CommonJS
  external: [
    'dotenv',
    'fs',
    'http',
    'https',
    'zod',
    'path',
    'buffer',
    'crypto',
    'url',
    'perf_hooks',
    'stream',
    'util'
  ],
  banner: {},
});
