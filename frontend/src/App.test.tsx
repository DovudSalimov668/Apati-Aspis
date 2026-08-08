import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Component', () => {
  it('renders application title and core scanner', async () => {
    render(<App />);
    expect(screen.getByText('Detect Digital Deception Before It Strikes')).toBeDefined();
  });
});
