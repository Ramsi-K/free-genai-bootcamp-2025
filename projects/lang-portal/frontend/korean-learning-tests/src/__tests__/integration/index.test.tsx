import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { MemoryRouter } from 'react-router-dom';
import App from '../../App'; // Adjust the import based on your app structure
import { server } from '../../mocks/server';
import { rest } from 'msw';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('Integration Tests', () => {
  test('completing a word practice session', async () => {
    render(
      <MockedProvider>
        <MemoryRouter initialEntries={['/word-practice']}>
          <App />
        </MemoryRouter>
      </MockedProvider>
    );

    // Simulate user interactions
    const startButton = screen.getByRole('button', { name: /start practice/i });
    fireEvent.click(startButton);

    // Wait for the practice session to load
    await waitFor(() => expect(screen.getByText(/practice session/i)).toBeInTheDocument());

    // Simulate answering a question
    const answerInput = screen.getByPlaceholderText(/type your answer/i);
    fireEvent.change(answerInput, { target: { value: 'correct answer' } });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    // Verify the result
    await waitFor(() => expect(screen.getByText(/correct!/i)).toBeInTheDocument());
  });

  test('switching practice types', async () => {
    render(
      <MockedProvider>
        <MemoryRouter initialEntries={['/word-practice']}>
          <App />
        </MemoryRouter>
      </MockedProvider>
    );

    const switchButton = screen.getByRole('button', { name: /switch to listening practice/i });
    fireEvent.click(switchButton);

    await waitFor(() => expect(screen.getByText(/listening practice/i)).toBeInTheDocument());
  });

  test('using semantic search', async () => {
    render(
      <MockedProvider>
        <MemoryRouter initialEntries={['/study-history']}>
          <App />
        </MemoryRouter>
      </MockedProvider>
    );

    const searchInput = screen.getByPlaceholderText(/search words/i);
    fireEvent.change(searchInput, { target: { value: 'example' } });
    fireEvent.click(screen.getByRole('button', { name: /search/i }));

    await waitFor(() => expect(screen.getByText(/example word/i)).toBeInTheDocument());
  });

  test('viewing study history', async () => {
    render(
      <MockedProvider>
        <MemoryRouter initialEntries={['/study-history']}>
          <App />
        </MemoryRouter>
      </MockedProvider>
    );

    await waitFor(() => expect(screen.getByText(/your study history/i)).toBeInTheDocument());
  });
});