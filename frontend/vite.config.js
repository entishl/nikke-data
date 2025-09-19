import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      open: true, // 在默认浏览器中打开分析报告
      gzipSize: true, // 显示 Gzip 压缩大小
      brotliSize: true, // 显示 Brotli 压缩大小
    }),
    viteCompression({
      verbose: true,
      disable: false,
      threshold: 10240, // 仅压缩大于 10kb 的文件
      algorithm: 'gzip',
      ext: '.gz',
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 15174,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        // configure: (proxy, options) => {
        //   // console.log('Proxying to:', options.target); // 可以在需要时取消注释
        // }
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          // 将 node_modules 中的依赖项打包到 vendor chunk 中
          if (id.includes('node_modules')) {
            return 'vendor';
          }
          // 将大型组件（如 DamageSimulation）单独打包
          if (id.includes('DamageSimulation.vue')) {
            return 'damage-simulation';
          }
        }
      }
    },
    terserOptions: {
      compress: {
        // 在生产环境中移除 console 和 debugger
        drop_console: true,
        drop_debugger: true,
      },
    },
  },
})
