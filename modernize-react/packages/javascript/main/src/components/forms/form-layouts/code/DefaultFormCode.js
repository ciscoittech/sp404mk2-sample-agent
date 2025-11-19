import CodeDialog from '../../../shared/CodeDialog';

const DefaultFormCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { FormControlLabel, Button, RadioGroup, FormControl, MenuItem } from '@mui/material';
import { Grid } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import { TextField } from '@mui/material';
import { Select } from '@mui/material';
import Radio, { RadioProps } from '@mui/material/Radio';
import Checkbox, { CheckboxProps } from '@mui/material/Checkbox';

const BpIcon = styled('span')(({ theme }) => ({
  borderRadius: 3,
  width: 19,
  height: 19,
  marginLeft: '4px',
  boxShadow:
    theme.palette.mode === 'dark'
      ? '0 0 0 1px {theme.palette.grey[200]}'
      : 'inset 0 0 0 1px {theme.palette.grey[300]}',
  backgroundColor: 'transparent',

  '.Mui-focusVisible &': {
    outline:
      theme.palette.mode === 'dark'
        ? '0px auto {theme.palette.grey[200]}'
        : '0px auto  {theme.palette.grey[300]}',
    outlineOffset: 2,
  },
  'input:hover ~ &': {
    backgroundColor: theme.palette.mode === 'dark' ? theme.palette.primary : theme.palette.primary,
  },
  'input:disabled ~ &': {
    boxShadow: 'none',
    background: theme.palette.grey[100],
  },
}));

const BpCheckedIcon = styled(BpIcon)({
  boxShadow: 'none',
  width: 19,
  height: 19,
  '&:before': {
    display: 'block',
    width: 19,
    height: 19,
    backgroundImage:
      "url(\"data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath" +
      " fill-rule='evenodd' clip-rule='evenodd' d='M12 5c-.28 0-.53.11-.71.29L7 9.59l-2.29-2.3a1.003 " +
      "1.003 0 00-1.42 1.42l3 3c.18.18.43.29.71.29s.53-.11.71-.29l5-5A1.003 1.003 0 0012 5z' fill='%23fff'/%3E%3C/svg%3E\")",
    content: '""',
  },
});

const BpIcon2 = styled('span')(({ theme }) => ({
  borderRadius: '50%',
  width: 21,
  height: 21,
  boxShadow:
    theme.palette.mode === 'dark'
      ? '0 0 0 1px {theme.palette.grey[200]}'
      : 'inset 0 0 0 1px {theme.palette.grey[300]}',
  backgroundColor: 'transparent',
  '.Mui-focusVisible &': {
    outline:
      theme.palette.mode === 'dark'
        ? '0px auto {theme.palette.grey[200]}'
        : '0px auto  {theme.palette.grey[300]}',
    outlineOffset: 2,
  },
  'input:hover ~ &': {
    backgroundColor: theme.palette.primary,
  },
  'input:disabled ~ &': {
    boxShadow: 'none',
    background: theme.palette.grey[100],
  },
}));

const BpCheckedIcon2 = styled(BpIcon2)(({ theme }) => ({
  boxShadow: 'none',
  '&:before': {
    display: 'block',
    width: 21,
    height: 21,
    backgroundImage:
      theme.palette.mode === 'dark'
        ? 'radial-gradient({theme.palette.background.paper},{theme.palette.background.paper} 28%,transparent 32%)'
        : 'radial-gradient(#fff,#fff 28%,transparent 32%)',
    content: '""',
  },
}));

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

const CustomFormLabel = styled((props) => (
  <Typography
    variant="subtitle1"
    fontWeight={600}
    {...props}
    component="label"
    htmlFor={props.htmlFor}
  />
))(() => ({
  marginBottom: '5px',
  marginTop: '25px',
  display: 'block',
}));

const CustomSelect = styled((props) => <Select {...props} />)(({}) => ({}));

function CustomCheckbox(props: CheckboxProps) {
  return (
    <Checkbox
      disableRipple
      color={props.color ? props.color : 'default'}
      checkedIcon={
        <BpCheckedIcon
          sx={{
            backgroundColor: props.color ? '{props.color}.main' : 'primary.main',
          }}
        />
      }
      icon={<BpIcon />}
      inputProps={{ 'aria-label': 'Checkbox demo' }}
      {...props}
    />
  );
}

function CustomRadio(props: RadioProps) {
  return (
    <Radio
      disableRipple
      color="default"
      checkedIcon={
        <BpCheckedIcon2
          sx={{
            backgroundColor: props.color ? '{props.color}.main' : 'primary.main',
          }}
        />
      }
      icon={<BpIcon2 />}
      inputProps={{ 'aria-label': 'Checkbox demo' }}
      {...props}
    />
  );
}

const numbers = [
  {
    value: 'one',
    label: 'One',
  },
  {
    value: 'two',
    label: 'Two',
  },
  {
    value: 'three',
    label: 'Three',
  },
  {
    value: 'four',
    label: 'Four',
  },
];

const [state, setState] = React.useState({
    checkedA: false,
    checkedB: false,
    checkedC: false,
});

const handleChange = (event) => {
    setState({ ...state, [event.target.name]: event.target.checked });
};

const [value, setValue] = React.useState('');

const handleChange2 = (event) => {
    setValue(event.target.value);
};

const [number, setNumber] = React.useState('');

const handleChange3 = (event) => {
    setNumber(event.target.value);
};

<form>
  <CustomFormLabel
    sx={{
      mt: 0,
    }}
    htmlFor="default-value"
  >
    Default Text
  </CustomFormLabel>
  <CustomTextField
    id="default-value"
    variant="outlined"
    defaultValue="George deo"
    fullWidth
  />
  <CustomFormLabel htmlFor="email-text">Email</CustomFormLabel>
  <CustomTextField id="email-text" type="email" variant="outlined" fullWidth />
  <CustomFormLabel htmlFor="default-outlined-password-input">Password</CustomFormLabel>

  <CustomTextField
    id="default-outlined-password-input"
    type="password"
    autoComplete="current-password"
    variant="outlined"
    fullWidth
  />
  <CustomFormLabel htmlFor="outlined-multiline-static">Textarea</CustomFormLabel>

  <CustomTextField
    id="outlined-multiline-static"
    multiline
    rows={4}
    variant="outlined"
    fullWidth
  />
  <CustomFormLabel htmlFor="readonly-text">Read Only</CustomFormLabel>

  <CustomTextField
    id="readonly-text"
    defaultValue="Hello World"
    slotProps={{
      input: {
        readOnly: true,
      },
    }}
    variant="outlined"
    fullWidth
  />
  <Grid container spacing={0} my={2}>
    <Grid size={{ lg: 4, md: 6, sm: 12 }}>
      <FormControlLabel
        control={
          <CustomCheckbox
            checked={state.checkedA}
            onChange={handleChange}
            name="checkedA"
            color="primary"
          />
        }
        label="Check this custom checkbox"
      />
      <FormControlLabel
        control={
          <CustomCheckbox
            checked={state.checkedB}
            onChange={handleChange}
            name="checkedB"
            color="primary"
          />
        }
        label="Check this custom checkbox"
      />
      <FormControlLabel
        control={
          <CustomCheckbox
            checked={state.checkedC}
            onChange={handleChange}
            name="checkedC"
            color="primary"
          />
        }
        label="Check this custom checkbox"
      />
    </Grid>
    <Grid size={{ lg: 4, md: 6, sm: 12 }}>
      <FormControl component="fieldset">
        <RadioGroup aria-label="gender" name="gender1" value={value} onChange={handleChange2}>
          <FormControlLabel
            value="radio1"
            control={<CustomRadio />}
            label="Toggle this custom radio"
          />
          <FormControlLabel
            value="radio2"
            control={<CustomRadio />}
            label="Toggle this custom radio"
          />
          <FormControlLabel
            value="radio3"
            control={<CustomRadio />}
            label="Toggle this custom radio"
          />
        </RadioGroup>
      </FormControl>
    </Grid>
  </Grid>
  <CustomFormLabel htmlFor="standard-select-number">Select</CustomFormLabel>
  <CustomSelect
    fullWidth
    id="standard-select-number"
    variant="outlined"
    value={number}
    onChange={handleChange3}
    sx={{
      mb: 2,
    }}
  >
    {numbers.map((option) => (
      <MenuItem key={option.value} value={option.value}>
        {option.label}
      </MenuItem>
    ))}
  </CustomSelect>
  <div>
    <Button color="primary" variant="contained">
      Submit
    </Button>
  </div>
  </form>
`}
      </CodeDialog>
    </>
  );
};

export default DefaultFormCode;
