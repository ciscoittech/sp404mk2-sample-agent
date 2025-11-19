import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const ControlledStateCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { styled } from '@mui/material/styles';
import { TextField } from '@mui/material';
import Autocomplete from '@mui/material/Autocomplete';

const CustomTextField = styled((props) => <TextField {...props} />)(({ theme }) => ({
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

const options = ['Option 1', 'Option 2'];

const [value, setValue] = React.useState(options[0]);
const [inputValue, setInputValue] = React.useState('');

<Autocomplete
    value={value}
    onChange={(event, newValue) => {
          setValue(newValue);
    }}
    inputValue={inputValue}
    onInputChange={(event, newInputValue) => {
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
    >{'value: {value !== null ? ''{value}'' : 'null'}'}
</Typography>
<Typography
    color="textSecondary"
    variant="subtitle2"
    >{'inputvalue: '{inputValue}''}
</Typography>`}
      </CodeDialog>
    </>
  );
};

export default ControlledStateCode;
