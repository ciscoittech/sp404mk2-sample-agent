import CodeDialog from '../../../shared/CodeDialog';

const LeftIconFormCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import {
  Button,
  FormControlLabel,
  FormControl,
  InputAdornment,
  OutlinedInput,
  Stack
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import Checkbox, { CheckboxProps } from '@mui/material/Checkbox';
import { IconLock, IconMail, IconUser } from '@tabler/icons';

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

// Inspired by blueprintjs
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

const [state, setState] = React.useState({
    checkedA: false,
});

const handleChange = (event) => {
    setState({ ...state, [event.target.name]: event.target.checked });
};

<form>
    <FormControl fullWidth>
        <CustomFormLabel
            sx={{
              mt: 0,
            }}
            htmlFor="username-text"
        >
            Username
        </CustomFormLabel>
        <OutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconUser width={20} />
              </InputAdornment>
            }
            id="username-text"
            placeholder="Username"
            fullWidth
        />
    </FormControl>
    <FormControl fullWidth>
        <CustomFormLabel htmlFor="mail-text">Email</CustomFormLabel>
        <OutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconMail width={20} />
              </InputAdornment>
            }
            id="mail-text"
            placeholder="Email"
            fullWidth
        />
    </FormControl>
    <FormControl fullWidth>
        <CustomFormLabel htmlFor="pwd-text">Password</CustomFormLabel>
        <OutlinedInput
            type="password"
            startAdornment={
              <InputAdornment position="start">
                <IconLock width={20} />
              </InputAdornment>
            }
            id="pwd-text"
            placeholder="Password"
            fullWidth
        />
    </FormControl>
    <FormControl fullWidth>
        <CustomFormLabel htmlFor="cpwd-text">Confirm Password</CustomFormLabel>
        <OutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconLock width={20} />
              </InputAdornment>
            }
            id="cpwd-text"
            placeholder="Confirm Password"
            fullWidth
        />
    </FormControl>

    <FormControlLabel
        control={
            <CustomCheckbox checked={state.checkedA} onChange={handleChange} name="checkedA" />
        }
        sx={{
            mt: '10px',
        }}
        label="Remember Me!"
    />
</form>

<Stack direction="row" spacing={2}>
  <Button
    color="primary"
    variant="contained">
    Submit
  </Button>
  <Button variant="contained" color="error">
    Cancel
  </Button>
</Stack>
`}
      </CodeDialog>
    </>
  );
};

export default LeftIconFormCode;
