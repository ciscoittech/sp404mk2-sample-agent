import CodeDialog from 'src/components/shared/CodeDialog';
const BasicDateTimeCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";
import React from 'react';
import dayjs, { Dayjs } from 'dayjs';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker';
import { styled } from '@mui/material/styles';
import { TextField } from '@mui/material';

const CustomTextField = styled((props: any) => <TextField {...props} />)(({ theme }) => ({
  '& .MuiOutlinedInput-input::-webkit-input-placeholder': {
    color: theme.palette.text.secondary,
    opacity: '0.8',
  },
  '& .MuiOutlinedInput-input.Mui-disabled::-webkit-input-placeholder': {
    color: theme.palette.text.secondary,
    opacity: '1',
  },
  '& .Mui-disabled .MuiOutlinedInput-notchedOutline': {
    borderColor: theme.palette.grey[200],
  },
}));

const [value3, setValue3] = React.useState<Dayjs | null>(
    dayjs("2018-01-01T00:00:00.000Z")
  );

<LocalizationProvider dateAdapter={AdapterDayjs}>
  <MobileDateTimePicker
    onChange={(newValue) => {
      setValue3(newValue)
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
`}
      </CodeDialog>
    </>
  );
};

export default BasicDateTimeCode;
