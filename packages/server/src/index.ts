import { buildServer } from './server.ts';

const server = buildServer();
const port = Number(process.env['PORT'] ?? 3000);

await server.listen({ port, host: '0.0.0.0' });
