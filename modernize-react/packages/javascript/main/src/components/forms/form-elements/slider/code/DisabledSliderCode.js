import CodeDialog from '../../../../shared/CodeDialog';

const DisabledSliderCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Slider } from '@mui/material';

<Slider disabled defaultValue={30} aria-label="slider" />
`}
      </CodeDialog>
    </>
  );
};

export default DisabledSliderCode;
