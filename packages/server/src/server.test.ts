import { buildServer } from './server.ts';

describe('buildServer', () => {
  // Close in a finally so a failing assertion still releases the instance. Nothing
  // is held today, but the route tests in #30 will copy this shape and those
  // instances own database handles.
  it('answers an unknown route with 404', async () => {
    const server = buildServer();

    try {
      const response = await server.inject({ method: 'GET', url: '/nope' });

      expect(response.statusCode).toBe(404);
    } finally {
      await server.close();
    }
  });
});
