import type { Todo } from '@todo/shared';

// Structural: it asserts that the shared package resolves by name from the web
// workspace, with no relative path crossing a package boundary. Superseded once
// the client actually consumes the API types (#34).
describe('@todo/shared', () => {
  it('resolves by package name from the web workspace', () => {
    const todo: Todo = { id: '1', title: 'Buy milk', completed: false };

    expect(todo.completed).toBe(false);
  });
});
