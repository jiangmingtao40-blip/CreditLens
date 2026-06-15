const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const AI_SERVICE = 'http://localhost:8081';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  
  // API代理 - 转发到AI服务
  if (url.pathname.startsWith('/api/')) {
    const targetUrl = `${AI_SERVICE}${url.pathname}`;
    
    console.log(`[Proxy] ${req.method} ${targetUrl}`);
    
    const options = {
      hostname: 'localhost',
      port: 8081,
      path: url.pathname,
      method: req.method,
      headers: {
        'Content-Type': req.headers['content-type'] || 'application/json'
      }
    };
    
    const proxyReq = http.request(options, (proxyRes) => {
      let data = '';
      proxyRes.on('data', chunk => data += chunk);
      proxyRes.on('end', () => {
        res.writeHead(proxyRes.statusCode, {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        });
        res.end(data);
      });
    });
    
    proxyReq.on('error', (err) => {
      console.error('Proxy error:', err);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: '服务不可用' }));
    });
    
    if (req.method === 'POST' || req.method === 'PUT') {
      req.pipe(proxyReq);
    } else {
      proxyReq.end();
    }
    return;
  }
  
  // 静态文件服务
  let filePath = path.join(__dirname, url.pathname === '/' ? 'index.html' : url.pathname);
  
  const ext = path.extname(filePath).toLowerCase();
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';
  
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/html' });
        res.end('<h1>404 Not Found</h1>');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/html' });
        res.end('<h1>500 Server Error</h1>');
      }
      return;
    }
    
    res.writeHead(200, {
      'Content-Type': contentType,
      'Access-Control-Allow-Origin': '*'
    });
    res.end(content);
  });
});

server.listen(PORT, () => {
  console.log(`\n========================================`);
  console.log(`  信用解析原型服务已启动`);
  console.log(`  访问地址: http://localhost:${PORT}`);
  console.log(`  AI服务: ${AI_SERVICE}`);
  console.log(`========================================\n`);
});
