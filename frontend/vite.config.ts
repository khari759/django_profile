import react from "@vitejs/plugin-react";
// vitest/config re-exports Vite's defineConfig with the `test` block typed.
import { defineConfig } from "vitest/config";

export default defineConfig({
  // GitHub Pages serves the site from /<repo-name>/, so asset URLs need that
  // prefix. The deploy workflow sets VITE_BASE_PATH; local dev stays at "/".
  base: process.env.VITE_BASE_PATH ?? "/",
  plugins: [react()],
  server: {
    port: 5173,
    // Fail loudly rather than silently moving to another port, so the
    // backend's CORS allow-list stays correct.
    strictPort: true,
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
    css: false,
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/main.tsx", "src/**/*.test.{ts,tsx}", "src/types.ts"],
    },
  },
});
