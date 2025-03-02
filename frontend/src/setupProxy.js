const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://backend:5000',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '/api',
      },
      onError: (err, req, res) => {
        console.error('Proxy Detailed Error:', {
          message: err.message,
          code: err.code,
          stack: err.stack,
          request: {
            method: req.method,
            url: req.url,
            headers: req.headers
          }
        });
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          error: 'Proxy Error', 
          message: err.message,
          code: err.code
        }));
      },
      // Add more detailed logging
      logLevel: 'debug'
    })
  );
};
