import CodeDialog from 'src/components/shared/CodeDialog';
const VolumesliderCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";
import React from "react";
import { Slider } from '@mui/material';
import { IconVolume, IconVolume2 } from '@tabler/icons-react';
import { Stack } from "@mui/system";
import { styled } from '@mui/material/styles';


const CustomSlider = styled(Slider)(({ theme }) => ({
  '& .MuiSlider-rail': {
    height: '9px',
    borderRadius: '9px',
    opacity: '1',
    backgroundColor: theme.palette.grey[200],
  },
  '& .MuiSlider-thumb': {
    borderRadius: '50%',
    backgroundColor: () => theme.palette.secondary.main,
    width: '23px',
    height: '23px',
  },
  '& .MuiSlider-track': {
    height: '9px',
    borderRadius: '9px',
  },
}));

const [value, setValue] = React.useState(30);
  const handleChange = (event: any, newValue: any) => {
    setValue(newValue);

 <Stack direction="row" spacing={1}>
    <IconVolume2 width={20} />
    <Slider aria-label="Volume" value={value} onChange={handleChange} />
    <IconVolume width={20} />
  </Stack>
`}
      </CodeDialog>
    </>
  );
};

export default VolumesliderCode;
