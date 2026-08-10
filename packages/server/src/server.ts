import Fastify, { type FastifyInstance } from 'fastify';

/**
 * Builds the application instance. It carries no routes yet — the todo
 * endpoints are #30 — so everything answers Fastify's built-in 404.
 *
 * Tests build their own instance and drive it with `inject`, which is why this
 * is separate from the entry point that listens.
 */
export function buildServer(): FastifyInstance {
  return Fastify({ logger: false });
}
