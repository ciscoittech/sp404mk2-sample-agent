import React from 'react';
import { Box, FormControlLabel } from '@mui/material';
// custom
import CustomCheckbox from '../../theme-elements/CustomCheckbox';

const label = { inputProps: { 'aria-label': 'checkbox with default color' } };

const ColorsCheckbox = () => (
  <Box textAlign="center">
    <FormControlLabel control={<CustomCheckbox defaultChecked />} label="Primary" />
    <FormControlLabel
      control={<CustomCheckbox defaultChecked bgcolor="secondary" {...label} />}
      label="Secondary"
    />
    <FormControlLabel
      control={<CustomCheckbox defaultChecked bgcolor="success" {...label} />}
      label="Success"
    />
    <FormControlLabel
      control={<CustomCheckbox defaultChecked bgcolor="warning" {...label} />}
      label="Warning"
    />
    <FormControlLabel
      control={<CustomCheckbox defaultChecked bgcolor="error" {...label} />}
      label="Error"
    />
  </Box>
);

export default ColorsCheckbox;
