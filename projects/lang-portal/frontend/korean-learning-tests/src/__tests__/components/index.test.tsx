import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import WordPractice from '../../components/WordPractice';
import ListeningPractice from '../../components/ListeningPractice';
import SentencePractice from '../../components/SentencePractice';
import Dashboard from '../../components/Dashboard';

describe('Component Tests', () => {
  test('renders WordPractice component and marks words correctly', () => {
    render(<WordPractice />);
    const wordElement = screen.getByText(/example word/i);
    fireEvent.click(wordElement);
    expect(wordElement).toHaveClass('correct');
  });

  test('renders ListeningPractice component and plays audio', () => {
    render(<ListeningPractice />);
    const playButton = screen.getByRole('button', { name: /play audio/i });
    fireEvent.click(playButton);
    expect(screen.getByText(/audio is playing/i)).toBeInTheDocument();
  });

  test('renders SentencePractice component and checks sentence correctness', () => {
    render(<SentencePractice />);
    const sentenceInput = screen.getByPlaceholderText(/type your sentence/i);
    fireEvent.change(sentenceInput, { target: { value: 'Correct sentence' } });
    expect(screen.getByText(/correct!/i)).toBeInTheDocument();
  });

  test('renders Dashboard component and displays user progress', () => {
    render(<Dashboard />);
    expect(screen.getByText(/your progress/i)).toBeInTheDocument();
  });
});