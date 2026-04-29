import { defineConfig } from '@umijs/max';
import { codeInspectorPlugin } from 'code-inspector-plugin';
import path from 'path';
import routes from '../src/routes';

const PUBLIC_PATH = '/';

export default defineConfig({
  chainWebpack (memo: any) {
    memo.plugin('code-inspector-plugin').use(
      codeInspectorPlugin({
        bundler: 'webpack',
      }),
    );
  },
  publicPath: PUBLIC_PATH,
  access: {},
  model: {},
  initialState: {},
  request: {},
  layout: {},
  title: 'My Python AI App',
  routes,
  npmClient: 'pnpm',
  alias: {
    '@/': path.resolve(__dirname, '../src'),
  },
  tailwindcss: {},
  mfsu: {},
  esbuildMinifyIIFE: true,
  favicons: [`${PUBLIC_PATH}favicon.ico`],
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
    },
  },
});
