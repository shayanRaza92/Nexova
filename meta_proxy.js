const http = require('http');

const VERIFY_TOKEN = 'nexova_verify';
const N8N_PORT = 5678;

const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://localhost');

    // Handle Meta verification (GET request)
    if (req.method === 'GET' && url.searchParams.get('hub.verify_token') === VERIFY_TOKEN) {
        console.log('✅ Meta verification successful!');
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end(url.searchParams.get('hub.challenge'));
        return;
    }

    // Forward POST requests to n8n
    if (req.method === 'POST') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            console.log('📩 Forwarding message to n8n...');
            const n8nReq = http.request({
                hostname: 'localhost',
                port: N8N_PORT,
                path: req.url,
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }, n8nRes => {
                let responseBody = '';
                n8nRes.on('data', chunk => responseBody += chunk);
                n8nRes.on('end', () => {
                    res.writeHead(n8nRes.statusCode || 200);
                    res.end(responseBody);
                });
            });
            n8nReq.on('error', (err) => {
                console.log('❌ Error forwarding to n8n:', err.message);
                res.writeHead(500);
                res.end('Error forwarding to n8n');
            });
            n8nReq.write(body);
            n8nReq.end();
        });
        return;
    }

    res.writeHead(200);
    res.end('OK');
});

server.listen(3001, () => {
    console.log('🚀 Meta proxy running on port 3001');
    console.log('   → Handles verification GET requests');
    console.log('   → Forwards POST messages to n8n on port ' + N8N_PORT);
});
