import CodeDialog from '../../../../shared/CodeDialog';

const DefaultsliderCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Slider } from '@mui/material';

<Slider defaultValue={30} aria-label="slider" />
`}
      </CodeDialog>
    </>
  );
};

export default DefaultsliderCode;
