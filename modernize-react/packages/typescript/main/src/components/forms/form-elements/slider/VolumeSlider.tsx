"use client";

import React from "react";
import { Slider } from "@mui/material";
import ChildCard from 'src/components/shared/ChildCard'
import { IconVolume, IconVolume2 } from "@tabler/icons-react";
import { Stack } from "@mui/system";

import VolumesliderCode from "src/components/forms/form-elements/slider/code/VolumesliderCode";

const VolumeSlider = () => {
  const [value, setValue] = React.useState(30);
  const handleChange = (_event: any, newValue: any) => {
    setValue(newValue);
  };

  return (
    <ChildCard title="Volume" codeModel={<VolumesliderCode />}>
      <Stack direction="row" spacing={1}>
        <IconVolume2 width={20} />
        <Slider aria-label="Volume" value={value} onChange={handleChange} />
        <IconVolume width={20} />
      </Stack>
    </ChildCard>
  );
};

export default VolumeSlider;
