import React from 'react';
import { Box, Radio } from '@mui/material';

const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const DefaultRadio = () => {
  // 2
  const [checked, setChecked] = React.useState(true);

  const handleChange = (event) => {
    setChecked(event.target.checked);
  };

  return (
    <Box textAlign="center">
      <Radio checked={checked} onChange={handleChange} {...label} />

      <Radio disabled {...label} />
      <Radio color="default" {...label} />
    </Box>
  );
};

export default DefaultRadio;
