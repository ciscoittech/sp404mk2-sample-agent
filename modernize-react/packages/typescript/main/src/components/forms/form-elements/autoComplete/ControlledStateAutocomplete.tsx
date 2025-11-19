'use client'

import { Typography } from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';
import CustomTextField from "../../theme-elements/CustomTextField";
import React from 'react';

const options = ['Option 1', 'Option 2'];

const ControlledStateAutocomplete = () => {
  const [value, setValue] = React.useState<string | null>(options[0]);
  const [inputValue, setInputValue] = React.useState('');

  return (
    <>
      <Autocomplete
        value={value}
        onChange={(_event: any, newValue: string | null) => {
          setValue(newValue);
        }}
        inputValue={inputValue}
        onInputChange={(_event, newInputValue) => {
          setInputValue(newInputValue);
        }}
        id="controllable-states-demo"
        options={options}
        fullWidth
        renderInput={(params) => (
          <CustomTextField
            {...params}
            placeholder="Controllable"
            aria-label="Controllable"
          />
        )}
      />
      <Typography
        color="textSecondary"
        variant="subtitle2"
        sx={{
          mt: 1,
        }}
      >{`value: ${value !== null ? `'${value}'` : 'null'}`}</Typography>
      <Typography
        color="textSecondary"
        variant="subtitle2"
      >{`inputvalue: '${inputValue}'`}</Typography>
    </>
  );
};

export default ControlledStateAutocomplete;
