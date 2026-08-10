import { buildServer } from './server.ts';

describe('buildServer', () => {
  it('answers an unknown route with 404', async () => {
    const server = buildServer();

    const response = await server.inject({ method: 'GET', url: '/nope' });

    expect(response.statusCode).toBe(404);
    await server.close();
  });
});
