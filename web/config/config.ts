import { defineConfig } from '@umijs/max';
import { codeInspectorPlugin } from 'code-inspector-plugin';
import path from 'path';
import routes from '../src/routes';

const PUBLIC_PATH = '/';
const CODE_EDITOR_BIN = process.env.CODE_EDITOR || '/usr/local/bin/code';

export default defineConfig({
  chainWebpack (memo: any) {
    // Ensure IDE is deterministic for code-inspector runtime.
    process.env.CODE_EDITOR = process.env.CODE_EDITOR || CODE_EDITOR_BIN;

    memo.plugin('code-inspector-plugin').use(
      codeInspectorPlugin({
        editor: CODE_EDITOR_BIN as any,
        bundler: 'webpack',
        port: 6009,
        dev: process.env.NODE_ENV === 'development',
        hooks: {
          afterInspectRequest (options) {
            options.editor = (options.editor || CODE_EDITOR_BIN) as any;
            process.env.CODE_EDITOR = process.env.CODE_EDITOR || CODE_EDITOR_BIN;
          },
        },
        showSwitch: true,
        hideConsole: false,
        launchType: 'exec',
        openIn: 'reuse',
        pathType: 'absolute',
        mappings: [
          {
            find: /^web\//,
            replacement: '',
          },
        ],
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
    '/api/chat/stream': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
      timeout: 0,
      proxyTimeout: 0,
      // 接管响应管道，绕过 compression 中间件缓冲，逐 chunk 强制 flush
      selfHandleResponse: true,
      onProxyRes (proxyRes: any, _req: any, res: any) {
        // 转发原始响应头
        Object.keys(proxyRes.headers).forEach((key) => {
          const val = proxyRes.headers[key];
          if (val !== undefined) res.setHeader(key, val);
        });
        // 覆盖确保 SSE 所需头
        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');
        res.setHeader('X-Accel-Buffering', 'no');
        res.statusCode = proxyRes.statusCode ?? 200;

        proxyRes.on('data', (chunk: Buffer) => {
          res.write(chunk);
          // flush() 由 compression 中间件注入，调用可立即推送当前块
          if (typeof (res as any).flush === 'function') (res as any).flush();
        });
        proxyRes.on('end', () => res.end());
        proxyRes.on('error', () => res.end());
      },
    },
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true,
      pathRewrite: { '^/api': '' },
    },
  },
});
