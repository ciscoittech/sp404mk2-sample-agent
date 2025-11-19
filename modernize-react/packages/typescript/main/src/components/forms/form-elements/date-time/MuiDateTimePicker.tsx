'use client'

import React from 'react'
import dayjs, { Dayjs } from 'dayjs'
import ChildCard from 'src/components/shared/ChildCard'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { TimePicker } from '@mui/x-date-pickers/TimePicker'
import TimepickerCode from './code/TimepickerCode'
import { renderTimeViewClock } from '@mui/x-date-pickers/timeViewRenderers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'

const MuiDateTimePicker = () => {
  const [value2, setValue2] = React.useState<Dayjs | null>(dayjs())

  return (
    <ChildCard title='Timepicker' codeModel={<TimepickerCode />}>
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
  )
}

export default MuiDateTimePicker
