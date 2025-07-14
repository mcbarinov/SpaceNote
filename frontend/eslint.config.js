import js from "@eslint/js"
import globals from "globals"
import react from "eslint-plugin-react"
import reactHooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"
import jsxA11y from "eslint-plugin-jsx-a11y"
import tseslint from "@typescript-eslint/eslint-plugin"
import tsparser from "@typescript-eslint/parser"
import tanstackQuery from "@tanstack/eslint-plugin-query"

export default [
  { ignores: ["dist", "node_modules", "*.config.js"] },
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: 2022,
      globals: {
        ...globals.browser,
        ...globals.node,
      },
      parser: tsparser,
      parserOptions: {
        ecmaVersion: "latest",
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
        project: "./tsconfig.json",
      },
    },
    plugins: {
      "@typescript-eslint": tseslint,
      react: react,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      "jsx-a11y": jsxA11y,
      "@tanstack/query": tanstackQuery,
    },
    settings: {
      react: {
        version: "detect",
      },
    },
    rules: {
      // Base rules
      ...js.configs.recommended.rules,

      // TypeScript rules
      ...tseslint.configs.recommended.rules,
      "@typescript-eslint/no-unused-vars": ["error", { argsIgnorePattern: "^_" }],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/prefer-nullish-coalescing": "error",
      "@typescript-eslint/prefer-optional-chain": "error",
      "@typescript-eslint/consistent-type-imports": ["error", { prefer: "type-imports" }],

      // React rules
      ...react.configs.recommended.rules,
      ...react.configs["jsx-runtime"].rules,
      "react/prop-types": "off",
      "react/react-in-jsx-scope": "off",
      "react/jsx-uses-react": "off",
      "react/jsx-no-target-blank": ["error", { allowReferrer: false }],
      "react/jsx-curly-brace-presence": ["error", { props: "never", children: "never" }],

      // React Hooks rules
      ...reactHooks.configs.recommended.rules,

      // React Refresh
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],

      // Accessibility rules
      ...jsxA11y.configs.recommended.rules,

      // TanStack Query rules
      ...tanstackQuery.configs.recommended.rules,

      // Code style and consistency
      "prefer-const": "error",
      "no-var": "error",
      "object-shorthand": "error",
      "prefer-template": "error",
      "prefer-arrow-callback": "error",
      "prefer-destructuring": ["error", { object: true, array: false }],
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-debugger": "error",
      eqeqeq: ["error", "always"],
      curly: ["error", "all"],

      // Import/Export rules
      "sort-imports": ["error", { ignoreDeclarationSort: true }],

      // Quotes will be handled by Prettier
    },
  },
]
