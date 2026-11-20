import { defineConfig } from "vite";
export default defineConfig({
  root: "client",
  base: "./",
  build: { outDir: "../dist", emptyOutDir: true, sourcemap: false },
  server: { host: "127.0.0.1", proxy: { "/api": "http://127.0.0.1:3000" } },
});
