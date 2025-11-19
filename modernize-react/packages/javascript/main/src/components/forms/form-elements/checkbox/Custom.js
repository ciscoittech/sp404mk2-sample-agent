import React from 'react';
import { Box } from '@mui/material';
// custom
import CustomCheckbox from '../../theme-elements/CustomCheckbox';

const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const CustomEleCheckbox = () => {
  // 2
  const [checked, setChecked] = React.useState(true);

  const handleChange = (event) => {
    setChecked(event.target.checked);
  };
  return (
    <Box textAlign="center">
      <CustomCheckbox checked={checked} onChange={handleChange} {...label} />

      <CustomCheckbox disabled checked {...label} />
      <CustomCheckbox defaultChecked indeterminate color="secondary" {...label} />
      <CustomCheckbox defaultChecked color="default" {...label} />
    </Box>
  );
};

export default CustomEleCheckbox;
