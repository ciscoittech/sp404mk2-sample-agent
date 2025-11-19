import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const DefaultcolorsCheckboxCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Box, Checkbox } from '@mui/material';

const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

<Box textAlign="center">
    <Checkbox defaultChecked color="primary" {...label} />
    <Checkbox defaultChecked color="secondary" {...label} />
    <Checkbox
      defaultChecked
      sx={{
        color: (theme) => theme.palette.success.main,
        '&.Mui-checked': {
          color: (theme) => theme.palette.success.main,
        },
      }}
    />
    <Checkbox
      defaultChecked
      sx={{
        color: (theme) => theme.palette.error.main,
        '&.Mui-checked': {
          color: (theme) => theme.palette.error.main,
        },
      }}
    />
    <Checkbox
      defaultChecked
      sx={{
        color: (theme) => theme.palette.warning.main,
        '&.Mui-checked': {
          color: (theme) => theme.palette.warning.main,
        },
      }}
    />
  </Box>
`}
      </CodeDialog>
    </>
  );
};

export default DefaultcolorsCheckboxCode;
