import CodeDialog from 'src/components/shared/CodeDialog';
const DiscreteSliderCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";
import React from 'react';
import { Slider } from '@mui/material';

  function valuetext2(value: any) {
  return {value}°C;
}

  const [value2, setValue2] = React.useState([20, 37]);
  const handleChange2 = (event2: any, newValue2: any) => {
    setValue2(newValue2);
  };

<Slider
    getAriaLabel={() => 'Temperature range'}
    value={value2}
    onChange={handleChange2}
    valueLabelDisplay="auto"
    getAriaValueText={valuetext2}
/>
`}
      </CodeDialog>
    </>
  );
};

export default DiscreteSliderCode;
