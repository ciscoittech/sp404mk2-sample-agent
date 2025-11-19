// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid, Box, Slider, Typography, SliderThumb, SliderValueLabelProps, Stack } from '@mui/material';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import CustomRangeSlider from 'src/components/forms/theme-elements/CustomRangeSlider';
import CustomSlider from 'src/components/forms/theme-elements/CustomSlider';
import { IconVolume, IconVolume2 } from '@tabler/icons-react';

// codeModel
import CustomSliderCode from 'src/components/forms/form-elements/slider/code/CustomSliderCode';
import VolumesliderCode from 'src/components/forms/form-elements/slider/code/VolumesliderCode';
import RangesliderCode from 'src/components/forms/form-elements/slider/code/RangesliderCode';
import DefaultsliderCode from 'src/components/forms/form-elements/slider/code/DefaultsliderCode';
import DisabledSliderCode from 'src/components/forms/form-elements/slider/code/DisabledSliderCode';
import DiscreteSliderCode from 'src/components/forms/form-elements/slider/code/DiscreteSliderCode';
import TemperatureRangeCode from 'src/components/forms/form-elements/slider/code/TemperatureRangeCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Slider',
  },
];

const valuetext = (value: any) => `${value}°C`;

function valuetext2(value: any) {
  return `${value}°C`;
}

function AirbnbThumbComponent(props: SliderValueLabelProps) {
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
}

const MuiSlider = () => {
  const [value, setValue] = React.useState(30);
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const handleChange = (event: any, newValue: any) => {
    setValue(newValue);
  };
  const [value2, setValue2] = React.useState([20, 37]);
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  const handleChange2 = (event2: any, newValue2: any) => {
    setValue2(newValue2);
  };

  return (
    (<PageContainer title="Slider" description="this is Slider page">
      {/* breadcrumb */}
      <Breadcrumb title="Slider" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Slider">
        <Grid container spacing={3}>
          {/* ------------------------------------------------------------------- */}
          {/* Custom */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Custom" codeModel={<CustomSliderCode />}>
              <CustomSlider defaultValue={[30]} />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Volume */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Volume" codeModel={<VolumesliderCode />}>
              <CustomSlider defaultValue={30} aria-label="volume slider" />
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
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Range" codeModel={<RangesliderCode />}>
              <CustomRangeSlider
                slots={{ thumb: AirbnbThumbComponent }}
                getAriaLabel={(index: any) => (index === 0 ? 'Minimum price' : 'Maximum price')}
                defaultValue={[20, 40]}
              />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Default */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Default" codeModel={<DefaultsliderCode />}>
              <Slider defaultValue={30} />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Disabled */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Disabled" codeModel={<DisabledSliderCode />}>
              <Slider disabled defaultValue={30} />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Volume */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
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
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
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
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Range Default" codeModel={<TemperatureRangeCode />}>
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
    </PageContainer>)
  );
};

export default MuiSlider;
