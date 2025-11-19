import { setupWorker } from 'msw/browser';
import { accountHandlers } from './handlers/accountHandlers';

export const worker = setupWorker(...accountHandlers);
