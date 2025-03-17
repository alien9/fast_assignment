import { render, screen, container } from '@testing-library/react';
import App from './App';
import React from 'react'
import userEvent from '@testing-library/user-event'

//beforeAll(() => jest.spyOn(window, 'fetch'))

test('upload file', () => {
  const file = new File(['hello'], 'hello.png', {type: 'image/png'})
  render(<App />);

  const input = screen.getByLabelText(/upload file/i)
  userEvent.upload(input, file)

  expect(input.files[0]).toStrictEqual(file)
  expect(input.files.item(0)).toStrictEqual(file)
  expect(input.files).toHaveLength(1)
})

test('renders input field', ()=>{
  render(<App />);
  const inputElement=document.querySelector('input[type=file]');
  expect(inputElement).toBeInTheDocument();
})