'use client'

import React from 'react'
import dayjs, { Dayjs } from 'dayjs'

import ChildCard from 'src/components/shared/ChildCard'

import { LocalizationProvider } from '@mui/x-date-pickers'

import { MobileDateTimePicker } from '@mui/x-date-pickers/MobileDateTimePicker'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'

// codeModel
import BasicDateTimeCode from './code/BasicDateTimeCode'

const BasicDateTime = () => {
  // date time
  const [value3, setValue3] = React.useState<Dayjs | null>(
    dayjs('2018-01-01T00:00:00.000Z')
  )

  return (
    <ChildCard title='Basic' codeModel={<BasicDateTimeCode />}>
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
    </ChildCard>
  )
}

export default BasicDateTime
