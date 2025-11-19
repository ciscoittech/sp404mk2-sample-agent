'use client'

import React from 'react'
import { Slider } from '@mui/material'
import ChildCard from 'src/components/shared/ChildCard'


import TemperatureRangeCode from 'src/components/forms/form-elements/slider/code/TemperatureRangeCode'

function valuetext2(value: any) {
  return `${value}°C`
}

const RangeSlider = () => {
  const [value2, setValue2] = React.useState([20, 37])
  const handleChange2 = (_event2: any, newValue2: any) => {
    setValue2(newValue2)
  }

  return (
    <ChildCard title='Range Default' codeModel={<TemperatureRangeCode />}>
      <Slider
        getAriaLabel={() => 'Temperature range'}
        value={value2}
        onChange={handleChange2}
        valueLabelDisplay='auto'
        getAriaValueText={valuetext2}
      />
    </ChildCard>
  )
}

export default RangeSlider
