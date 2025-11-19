import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const DefaultRadioCode = () => {
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
    <Radio checked={checked} onChange={handleChange} {...label} />

    <Radio disabled {...label} />
    <Radio color="default" {...label} />
</Box>
`}
      </CodeDialog>
    </>
  );
};

export default DefaultRadioCode;
