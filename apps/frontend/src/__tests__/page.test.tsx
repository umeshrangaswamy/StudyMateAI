import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import Page from '../app/page';

describe('StudyMateDashboard Frontend UI Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('1. Page renders title StudyMateAI', () => {
    render(<Page />);
    const heading = screen.getByRole('heading', { name: /StudyMateAI/i });
    expect(heading).toBeInTheDocument();
  });

  test('2. Year dropdown renders', () => {
    render(<Page />);
    const dropdown = screen.getByLabelText(/Year of Study/i);
    expect(dropdown).toBeInTheDocument();
    expect(screen.getByText('2nd PUC / Class 12')).toBeInTheDocument();
  });

  test('3. Board dropdown renders', () => {
    render(<Page />);
    const dropdown = screen.getByLabelText(/University \/ Board/i);
    expect(dropdown).toBeInTheDocument();
    expect(screen.getByText('Karnataka State Board')).toBeInTheDocument();
  });

  test('4. Subject dropdown renders', () => {
    render(<Page />);
    const dropdown = screen.getByLabelText(/Subject/i);
    expect(dropdown).toBeInTheDocument();
    expect(screen.getByText('Physics')).toBeInTheDocument();
    expect(screen.getByText('Chemistry')).toBeInTheDocument();
  });

  test('5. Prompt text area renders', () => {
    render(<Page />);
    const textArea = screen.getByPlaceholderText(/e\.g\.,/i);
    expect(textArea).toBeInTheDocument();
  });

  test('6. Submit button is disabled if required fields are empty', () => {
    render(<Page />);
    // When prompt is empty by default
    const submitBtn = screen.getByRole('button', { name: /Ask Buddy/i });
    expect(submitBtn).toBeDisabled();
  });

  test('7. Submit button calls backend when all fields are present', async () => {
    const mockResponse = {
      answer: 'Ray Optics deals with light propagation in straight lines.',
      response_type: 'explanation',
      sources: [
        { document_title: 'NCERT Physics', chapter: 'Ray Optics', page_number: 104 }
      ],
      metadata: {
        subject: 'physics',
        intent: 'doubt_solving',
        exam: 'neet',
        confidence: 0.86
      }
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(<Page />);
    
    // Fill required prompt field
    const textArea = screen.getByPlaceholderText(/e\.g\.,/i);
    fireEvent.change(textArea, { target: { value: 'Explain refraction' } });

    const submitBtn = screen.getByRole('button', { name: /Ask Buddy/i });
    expect(submitBtn).not.toBeDisabled();
    
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  test('8. Response panel displays answer', async () => {
    const mockResponse = {
      answer: 'Covalent bonds share electrons.',
      response_type: 'explanation',
      sources: [],
      metadata: {
        subject: 'chemistry',
        intent: 'doubt_solving',
        confidence: 0.86
      }
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    render(<Page />);
    
    const textArea = screen.getByPlaceholderText(/e\.g\.,/i);
    fireEvent.change(textArea, { target: { value: 'What is covalent bond?' } });

    const submitBtn = screen.getByRole('button', { name: /Ask Buddy/i });
    fireEvent.click(submitBtn);

    // Assert correct answer is shown
    await waitFor(() => {
      expect(screen.getByText(/Covalent bonds share electrons/i)).toBeInTheDocument();
    });
  });

  test('9. Error message displays on backend failure', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'API Limit Exceeded' }),
    });

    render(<Page />);
    
    const textArea = screen.getByPlaceholderText(/e\.g\.,/i);
    fireEvent.change(textArea, { target: { value: 'Explain optics' } });

    const submitBtn = screen.getByRole('button', { name: /Ask Buddy/i });
    fireEvent.click(submitBtn);

    // Assert error details are shown
    await waitFor(() => {
      expect(screen.getByText(/API Limit Exceeded/i)).toBeInTheDocument();
    });
  });
});
