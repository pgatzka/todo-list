import type { Todo } from '@todo/shared';
import { buildServer } from './server.ts';

describe('buildServer', () => {
  it('answers an unknown route with 404', async () => {
    const server = buildServer();

    const response = await server.inject({ method: 'GET', url: '/nope' });

    expect(response.statusCode).toBe(404);
    await server.close();
  });

  // Structural: it asserts that the shared package resolves by name from the
  // server workspace too. Superseded once the routes actually type their
  // payloads with it (#30).
  it('resolves @todo/shared by package name', () => {
    const todo: Todo = { id: '1', title: 'Buy milk', completed: false };

    expect(todo.title).toBe('Buy milk');
  });
});
