import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

export default defineConfig({
  plugins: [
    react(),
    // Custom plugin to serve dataf folder
    {
      name: 'serve-dataf',
      configureServer(server) {
        server.middlewares.use('/dataf', (req, res, next) => {
          const filePath = path.resolve(__dirname, '..', 'dataf', req.url || 'boeing_stock_topics_hd.html')
          if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath)
            const ext = path.extname(filePath)
            const contentType = ext === '.html' ? 'text/html' : 
                               ext === '.js' ? 'application/javascript' :
                               ext === '.css' ? 'text/css' :
                               ext === '.json' ? 'application/json' : 'text/plain'
            res.setHeader('Content-Type', contentType)
            res.end(content)
          } else {
            next()
          }
        })
      },
    },
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
