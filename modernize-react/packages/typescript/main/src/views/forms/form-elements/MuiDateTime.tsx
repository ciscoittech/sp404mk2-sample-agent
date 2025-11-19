// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import dayjs, { Dayjs } from 'dayjs';
import { Grid } from '@mui/material';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import { renderTimeViewClock } from '@mui/x-date-pickers/timeViewRenderers'

// codeModel
import BasicDateTimeCode from 'src/components/forms/form-elements/date-time/code/BasicDateTimeCode';
import DifferentDesignCode from 'src/components/forms/form-elements/date-time/code/DifferentDesignCode';
import TimepickerCode from 'src/components/forms/form-elements/date-time/code/TimepickerCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Date Time',
  },
];

const MuiDateTime = () => {
  const [value, setValue] = React.useState<Dayjs | null>(null);
  const [value2, setValue2] = React.useState<Dayjs | null>(null);

  // date time
  const [value3, setValue3] = React.useState<Dayjs | null>(dayjs('2018-01-01T00:00:00.000Z'));

  return (
    (<PageContainer title="Date Time" description="this is Date Time page">
      {/* breadcrumb */}
      <Breadcrumb title="Date Picker" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Date Time">
        <Grid container spacing={3}>
          {/* ------------------------------------------------------------------- */}
          {/* Basic */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 6,
              sm: 6
            }}>
            <ChildCard title="Basic" codeModel={<BasicDateTimeCode />}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <MobileDateTimePicker
                  onChange={(newValue) => {
                    setValue3(newValue);
                  }}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'outlined',
                      size: 'small',
                      inputProps: { 'aria-label': 'basic date picker' },
                    },
                  }}
                  value={value3}
                />
              </LocalizationProvider>
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Different */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 6,
              sm: 6
            }}>
            <ChildCard title="Different Design" codeModel={<DifferentDesignCode />}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <DateTimePicker
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      size: 'small',
                      sx: {
                        '& .MuiSvgIcon-root': {
                          width: '18px',
                          height: '18px',
                        },
                        '& .MuiFormHelperText-root': {
                          display: 'none',
                        },
                      },
                    },
                  }}
                  value={value}
                  onChange={(newValue) => {
                    setValue(newValue)
                  }}
                />
              </LocalizationProvider>
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Timepicker */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 6,
              sm: 6
            }}>
            <ChildCard title="Timepicker" codeModel={<TimepickerCode />}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <TimePicker
                  value={value2}
                  onChange={(newValue) => {
                    setValue2(newValue)
                  }}
                  viewRenderers={{
                    hours: renderTimeViewClock,
                    minutes: renderTimeViewClock,
                    seconds: renderTimeViewClock,
                  }}
                  slotProps={{
                    textField: {
                      size: 'small',
                      fullWidth: true,
                      sx: {
                        '& .MuiSvgIcon-root': {
                          width: '18px',
                          height: '18px',
                        },
                        '& .MuiFormHelperText-root': {
                          display: 'none',
                        },
                      },
                    },
                  }}
                />
              </LocalizationProvider>
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>)
  );
};

export default MuiDateTime;
