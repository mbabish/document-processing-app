const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy API requests to the backend
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://backend:5000',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '/api', // No rewrite needed since our backend already uses /api prefix
      },
      onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ 
          error: 'Proxy Error', 
          message: 'Could not connect to the API server' 
        }));
      }
    })
  );
};
