import CodeDialog from 'src/components/shared/CodeDialog';
const DiscreteSliderCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Slider } from '@mui/material';

const valuetext = (value: any) => {value}°C;

<Slider
    aria-label="Temperature"
    defaultValue={30}
    getAriaValueText={valuetext}
    valueLabelDisplay="auto"
    step={10}
    marks
    min={10}
    max={110}
/>
`}
      </CodeDialog>
    </>
  );
};

export default DiscreteSliderCode;
