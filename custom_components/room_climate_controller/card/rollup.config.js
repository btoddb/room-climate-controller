import resolve from "@rollup/plugin-node-resolve";
import terser from "@rollup/plugin-terser";
import typescript from "@rollup/plugin-typescript";

export default {
  input: "src/index.ts",
  output: {
    file: "room-climate-control-card.js",
    format: "es",
    sourcemap: true,
  },
  plugins: [typescript(), resolve(), terser()],
};
