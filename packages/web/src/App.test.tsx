import { render, screen } from '@testing-library/react';
import App from './App';

/**
 * Smoke test for the scaffold. Its job is to prove the harness itself works —
 * that JSX compiles, jsdom renders, Testing Library queries resolve and the
 * jest-dom matchers are registered. Behavioural tests arrive with M1.
 */
describe('App', () => {
  it('renders the application heading', () => {
    render(<App />);

    expect(screen.getByRole('heading', { level: 1, name: 'todo-list' })).toBeInTheDocument();
  });

  it('renders its content inside a main landmark', () => {
    render(<App />);

    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
