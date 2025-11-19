import React from 'react';
import { Box } from '@mui/material';

import CustomRadio from '../../theme-elements/CustomRadio';

const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const CustomExRadio = () => {
  // 2
  const [checked, setChecked] = React.useState(true);

  const handleChange = (event) => {
    setChecked(event.target.checked);
  };

  return (
    <Box textAlign="center">
      <CustomRadio checked={checked} onChange={handleChange} {...label} />

      <CustomRadio disabled {...label} />
      <CustomRadio color="default" {...label} />
    </Box>
  );
};

export default CustomExRadio;
