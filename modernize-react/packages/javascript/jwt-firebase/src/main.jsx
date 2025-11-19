import React, { Suspense } from "react";
import { CustomizerContextProvider } from './context/CustomizerContext';
import ReactDOM from "react-dom/client";
import App from "./App";
import Spinner from "./views/spinner/Spinner";
import "./utils/i18n";
import { AuthProvider } from "src/guards/auth/AuthContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <CustomizerContextProvider>
    <Suspense fallback={<Spinner />}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Suspense>
  </CustomizerContextProvider>
);
