import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  it('renders application title', async () => {
    render(<App />);
    expect(screen.getByText('APATI ASPIS')).toBeDefined();
    expect(screen.getByText('Detect Deception Before It Strikes')).toBeDefined();
    
    await waitFor(() => {
      expect(screen.queryByText('Connecting to APATI ASPIS API server...')).toBeNull();
    });
  });
});
