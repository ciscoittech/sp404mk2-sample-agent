// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { Suspense } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import Spinner from './views/spinner/Spinner';
import './utils/i18n';
import { CustomizerContextProvider } from 'src/context/CustomizerContext.tsx'
import { AuthProvider } from 'src/guards/auth/AuthContext.tsx';

async function deferRender() {
  const { worker } = await import('./api/mocks/browser.ts');
  return worker.start({
    onUnhandledRequest: 'bypass',
  });
}

deferRender().then(() => {
  ReactDOM.createRoot(document.getElementById('root')!).render(
    <CustomizerContextProvider>
      <Suspense fallback={<Spinner />}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </Suspense>
    </CustomizerContextProvider>,
  )
})

