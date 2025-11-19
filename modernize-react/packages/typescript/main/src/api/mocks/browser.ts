import { setupWorker } from 'msw/browser';
import { mockHandlers } from './handlers/mockhandlers';

export const worker = setupWorker(...mockHandlers);
