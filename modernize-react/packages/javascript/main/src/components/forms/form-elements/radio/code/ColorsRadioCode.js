import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const ColorsRadioCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Box, Radio } from '@mui/material';

const label = { inputProps: { 'aria-label': 'Checkbox demo' } };

const [checked, setChecked] = React.useState(true);

const handleChange = (event) => {
    setChecked(event.target.checked);
};

<Box textAlign="center">
      <Radio checked={checked} onChange={handleChange} color="primary" {...label} />

      <Radio checked={checked} onChange={handleChange} color="secondary" {...label} />

      <Radio
        checked={checked}
        onChange={handleChange}
        {...label}
        sx={{
          color: (theme) => theme.palette.success.main,
          '&.Mui-checked': {
            color: (theme) => theme.palette.success.main,
          },
        }}
      />

      <Radio
        checked={checked}
        onChange={handleChange}
        {...label}
        sx={{
          color: (theme) => theme.palette.error.main,
          '&.Mui-checked': {
            color: (theme) => theme.palette.error.main,
          },
        }}
      />

      <Radio
        checked={checked}
        onChange={handleChange}
        {...label}
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

export default ColorsRadioCode;
