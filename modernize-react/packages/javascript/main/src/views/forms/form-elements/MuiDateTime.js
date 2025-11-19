import React from 'react';
import { Grid } from '@mui/material';
import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';
import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';
import CustomTextField from '../../../components/forms/theme-elements/CustomTextField';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { TimePicker } from '@mui/x-date-pickers/TimePicker';
import dayjs from 'dayjs'
import { renderTimeViewClock } from '@mui/x-date-pickers/timeViewRenderers'

// codeModel
import BasicDateTimeCode from '../../../components/forms/form-elements/date-time/code/BasicDateTimeCode';
import DifferentDesignCode from '../../../components/forms/form-elements/date-time/code/DifferentDesignCode';
import TimepickerCode from '../../../components/forms/form-elements/date-time/code/TimepickerCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Date Time',
  },
];

const ExDateTime = () => {
  const [value, setValue] = React.useState(dayjs());
  const [value2, setValue2] = React.useState(dayjs())

  return (
    <PageContainer title="Date Time" description="this is Date Time page">
      {/* breadcrumb */}
      <Breadcrumb title="Date Picker" items={BCrumb} />
      {/* end breadcrumb */}

      <ParentCard title="Date Time">
        <Grid container spacing={3}>
          {/* ------------------------------------------------------------------- */}
          {/* Basic */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Basic" codeModel={<BasicDateTimeCode />}>
              <LocalizationProvider dateAdapter={AdapterDayjs}>
                <MobileDateTimePicker
                  onChange={(newValue) => {
                    setValue(newValue)
                  }}
                  slotProps={{
                    textField: {
                      fullWidth: true,
                      variant: 'outlined',
                      size: 'small',
                      inputProps: { 'aria-label': 'basic date picker' },
                    },
                  }}
                  value={value}
                />
              </LocalizationProvider>
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Different */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
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
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
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
    </PageContainer>
  );
};

export default ExDateTime;
