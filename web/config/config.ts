import { defineConfig } from '@umijs/max';
import { codeInspectorPlugin } from 'code-inspector-plugin';
import path from 'path';
import routes from '../src/routes';

const PUBLIC_PATH = '/lawai-chat/';

export default defineConfig({
  chainWebpack(memo: any) {
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
  title: 'AI合规助手',
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
    '/api/announce/qa/chat/stream': {
      target: 'https://test-disclosure.goldmye.com',
      changeOrigin: true,
      selfHandleResponse: false,
      onProxyReq(proxyReq: any) {
        // 禁止 gzip 压缩，防止代理层聚合 SSE chunk
        proxyReq.setHeader('accept-encoding', 'identity');
        proxyReq.setHeader('connection', 'keep-alive');
      },
      onProxyRes(proxyRes: any) {
        // 告知所有中间层（Nginx/代理）不要缓冲
        proxyRes.headers['x-accel-buffering'] = 'no';
        // 禁止缓存和压缩转换
        proxyRes.headers['cache-control'] = 'no-cache, no-transform';
        // 强制 SSE content-type
        proxyRes.headers['content-type'] = 'text/event-stream; charset=utf-8';
      },
    },
    '/api': {
      target: 'https://test-disclosure.goldmye.com',
      changeOrigin: true,
    },
  },
});
