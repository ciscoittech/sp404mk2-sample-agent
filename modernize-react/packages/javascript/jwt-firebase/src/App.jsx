
import { CustomizerContext } from 'src/context/CustomizerContext';
import { ThemeSettings } from './theme/Theme';
import RTL from './layouts/full/shared/customizer/RTL';
import { RouterProvider } from 'react-router';
import router from './routes/Router'
import { CssBaseline, ThemeProvider } from '@mui/material';
import { useContext } from 'react'

function App() {
  const theme = ThemeSettings();
  const { activeDir } = useContext(CustomizerContext);


  return (
    <ThemeProvider theme={theme}>
      <RTL direction={activeDir}>
        <CssBaseline />
        <RouterProvider router={router} />
      </RTL>
    </ThemeProvider>
  );
}

export default App
