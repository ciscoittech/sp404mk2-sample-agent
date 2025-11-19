'use client'
import React from 'react'

import ChildCard from 'src/components/shared/ChildCard'
import dayjs, { Dayjs } from 'dayjs'
import { LocalizationProvider } from '@mui/x-date-pickers'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker'

import DifferentDesignCode from './code/DifferentDesignCode'

const DifferentDateTime = () => {
  const [value, setValue] = React.useState<Dayjs | null>(dayjs())

  return (
    <ChildCard title='Different Design' codeModel={<DifferentDesignCode />}>
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
  )
}

export default DifferentDateTime
