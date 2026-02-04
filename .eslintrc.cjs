/** @type {import("eslint").Linter.Config} */
module.exports = {
  env: { node: true, es2022: true },
  parserOptions: { ecmaVersion: "latest", sourceType: "module" },
  ignorePatterns: ["dist", "node_modules"],
  extends: ["eslint:recommended"],
  rules: {
    "no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
    "no-console": "off"
  }
};
