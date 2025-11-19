import { styled } from '@mui/material/styles';
import { Button } from '@mui/material';

const CustomOutlinedButton =  styled((Button))(({ theme })  => ({
  border: `${
    theme.palette.mode === 'dark'
      ? '1px solid rgba(255, 255, 255, 0.2)'
      : '1px solid rgba(73,82,88,0.12)'
  }`,

  color: `${theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.5)' : 'rgba(73,82,88,0.5)'}`,
  '&:hover': {
    border: `${
      theme.palette.mode === 'dark'
        ? '1px solid rgba(255, 255, 255, 0.09)'
        : '1px solid rgba(73,82,88,0.12)'
    }`,
    backgroundColor: `${theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.09)' : '#ecf0f3'}`,
  },
}));

export default CustomOutlinedButton;
