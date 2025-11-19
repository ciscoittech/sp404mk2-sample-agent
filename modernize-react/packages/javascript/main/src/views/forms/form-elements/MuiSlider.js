import React from 'react';
import PropTypes from 'prop-types';
import { Grid } from '@mui/material';
import Box from '@mui/system/Box';
import Slider from '@mui/material/Slider';
import Typography from '@mui/material/Typography';
import { SliderThumb } from '@mui/material/Slider';

import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';
import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';
import CustomRangeSlider from '../../../components/forms/theme-elements/CustomRangeSlider';
import CustomSlider from '../../../components/forms/theme-elements/CustomSlider';
import { IconVolume, IconVolume2 } from '@tabler/icons';
import { Stack } from '@mui/system';

// codeModel
import CustomSliderCode from '../../../components/forms/form-elements/slider/code/CustomSliderCode';
import VolumesliderCode from '../../../components/forms/form-elements/slider/code/VolumesliderCode';
import RangesliderCode from '../../../components/forms/form-elements/slider/code/RangesliderCode';
import DefaultsliderCode from '../../../components/forms/form-elements/slider/code/DefaultsliderCode';
import DisabledSliderCode from '../../../components/forms/form-elements/slider/code/DisabledSliderCode';
import DiscreteSliderCode from '../../../components/forms/form-elements/slider/code/DiscreteSliderCode';
import TemperatureRangeCode from '../../../components/forms/form-elements/slider/code/TemperatureRangeCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Slider',
  },
];

const valuetext = (value) => `${value}°C`;

function valuetext2(value) {
  return `${value}°C`;
}

const AirbnbThumbComponent = (props) => {
  const { children, ...other } = props;
  return (
    <SliderThumb {...other}>
      {children}
      <Box
        sx={{
          height: 9,
          width: '2px',
          backgroundColor: '#fff',
        }}
      />
      <Box
        sx={{
          height: '14px',
          width: '2px',
          backgroundColor: '#fff',
          ml: '2px',
        }}
      />
      <Box
        sx={{
          height: 9,
          width: '2px',
          backgroundColor: '#fff',
          ml: '2px',
        }}
      />
    </SliderThumb>
  );
};

AirbnbThumbComponent.propTypes = {
  children: PropTypes.node,
};

const ExSlider = () => {
  // 2
  const [value, setValue] = React.useState(30);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const [value2, setValue2] = React.useState([20, 37]);

  const handleChange2 = (event2, newValue2) => {
    setValue2(newValue2);
  };

  return (
    <PageContainer title="Slider" description="this is Slider page">
      {/* breadcrumb */}
      <Breadcrumb title="Slider" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Slider">
        <Grid container spacing={3}>
          {/* ------------------------------------------------------------------- */}
          {/* Custom */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Custom" codeModel={<CustomSliderCode />}>
              <CustomSlider defaultValue={30} aria-label="slider" />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Volume */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Volume" codeModel={<VolumesliderCode />}>
              <CustomSlider defaultValue={30} aria-label="slider" />
              <Box display="flex" alignItems="center">
                <Typography>
                  <IconVolume2 width={20} />
                </Typography>
                <Box ml="auto">
                  <Typography>
                    <IconVolume width={20} />
                  </Typography>
                </Box>
              </Box>
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Range */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Range" codeModel={<RangesliderCode />}>
              <CustomRangeSlider
                components={{ Thumb: AirbnbThumbComponent }}
                getAriaLabel={(index) => (index === 0 ? 'Minimum price' : 'Maximum price')}
                defaultValue={[20, 40]}
              />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Default */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Default" codeModel={<DefaultsliderCode />}>
              <Slider defaultValue={30} aria-label="slider" />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Disabled */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Disabled" codeModel={<DisabledSliderCode />}>
              <Slider disabled defaultValue={30} aria-label="slider" />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Volume */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Volume">
              <Stack direction="row" spacing={1}>
                <IconVolume2 width={20} />
                <Slider aria-label="Volume" value={value} onChange={handleChange} />
                <IconVolume width={20} />
              </Stack>
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Discrete */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Discrete" codeModel={<DiscreteSliderCode />}>
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
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Range Default */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Range Default" codeModel={<DiscreteSliderCode />}>
              <Slider
                getAriaLabel={() => 'Temperature range'}
                value={value2}
                onChange={handleChange2}
                valueLabelDisplay="auto"
                getAriaValueText={valuetext2}
              />
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>
  );
};

export default ExSlider;
