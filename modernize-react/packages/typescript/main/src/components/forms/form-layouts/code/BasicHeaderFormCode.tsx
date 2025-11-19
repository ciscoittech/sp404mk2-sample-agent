import CodeDialog from 'src/components/shared/CodeDialog';

const BasicHeaderFormCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";
import React from "react";
import {
  Box,
  FormControlLabel,
  Button,
 Grid,
  MenuItem,
  FormControl,
  Alert,
} from "@mui/material";
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import { TextField } from '@mui/material';
import { Select } from '@mui/material';
import Radio, { RadioProps } from '@mui/material/Radio';

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

const CustomFormLabel = styled((props: any) => (
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

const CustomSelect = styled((props: any) => <Select {...props} />)(({}) => ({}));

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

const currencies = [
  {
    value: 'female',
    label: 'Female',
  },
  {
    value: 'male',
    label: 'Male',
  },
  {
    value: 'other',
    label: 'Other',
  },
];

const countries = [
  {
    value: 'india',
    label: 'India',
  },
  {
    value: 'uk',
    label: 'United Kingdom',
  },
  {
    value: 'srilanka',
    label: 'Srilanka',
  },
];

const [currency, setCurrency] = React.useState('');

const handleChange2 = (event: any) => {
    setCurrency(event.target.value);
};

const [selectedValue, setSelectedValue] = React.useState('');

const handleChange3 = (event: any) => {
    setSelectedValue(event.target.value);
};

const [country, setCountry] = React.useState('');

const handleChange4 = (event: any) => {
    setCountry(event.target.value);
};

<div>
    <>
      <Alert severity="info">Person Info</Alert>
      <form>
        <Grid container spacing={3} mb={3}>
          <Grid
            size={{
              lg: 6,
              md: 12,
              sm: 12
            }}>
            <CustomFormLabel htmlFor="fname-text">
              First Name
            </CustomFormLabel>
            <CustomTextField id="fname-text" variant="outlined" fullWidth />
            <CustomFormLabel htmlFor="standard-select-currency">
              Select Gender
            </CustomFormLabel>
            <CustomSelect
              id="standard-select-currency"
              value={currency}
              onChange={handleChange2}
              fullWidth
              variant="outlined"
            >
              {currencies.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </CustomSelect>
            <CustomFormLabel>Membership</CustomFormLabel>

            <FormControl
              sx={{
                width: "100%",
              }}
            >
              <Box>
                <FormControlLabel
                  checked={selectedValue === "a"}
                  onChange={handleChange3}
                  value="a"
                  label="Free"
                  name="radio-button-demo"
                  control={<CustomRadio />}
                />
                <FormControlLabel
                  checked={selectedValue === "b"}
                  onChange={handleChange3}
                  value="b"
                  label="Paid"
                  control={<CustomRadio />}
                  name="radio-button-demo"
                />
              </Box>
            </FormControl>
          </Grid>
          <Grid
            size={{
              lg: 6,
              md: 12,
              sm: 12
            }}>
            <CustomFormLabel htmlFor="lname-text">
              Last Name
            </CustomFormLabel>

            <CustomTextField id="lname-text" variant="outlined" fullWidth />
            <CustomFormLabel htmlFor="date">Date of Birth</CustomFormLabel>

            <CustomTextField
              id="date"
              type="date"
              variant="outlined"
              fullWidth
              InputLabelProps={{
                shrink: true,
              }}
            />
          </Grid>
        </Grid>
      </form>
      <Alert severity="info">Address</Alert>
      <Grid container spacing={3} mb={3} mt={1}>
        <Grid
          size={{
            lg: 12,
            md: 12,
            sm: 12,
            xs: 12
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
            htmlFor="street-text"
          >
            Street
          </CustomFormLabel>

          <CustomTextField id="street-text" variant="outlined" fullWidth />
        </Grid>
        <Grid
          size={{
            lg: 6,
            md: 12,
            sm: 12,
            xs: 12
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
            htmlFor="city-text"
          >
            City
          </CustomFormLabel>
          <CustomTextField id="city-text" variant="outlined" fullWidth />
        </Grid>
        <Grid
          size={{
            lg: 6,
            md: 12,
            sm: 12,
            xs: 12
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
            htmlFor="state-text"
          >
            State
          </CustomFormLabel>
          <CustomTextField id="state-text" variant="outlined" fullWidth />
        </Grid>
        <Grid
          size={{
            lg: 6,
            md: 12,
            sm: 12,
            xs: 12
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
            htmlFor="post-text"
          >
            Post Code
          </CustomFormLabel>
          <CustomTextField id="post-text" variant="outlined" fullWidth />
        </Grid>
        <Grid
          size={{
            lg: 6,
            md: 12,
            sm: 12,
            xs: 12
          }}>
          <CustomFormLabel
            sx={{
              mt: 0,
            }}
            htmlFor="country-text"
          >
            Country
          </CustomFormLabel>
          <CustomSelect
            id="country-select"
            value={country}
            onChange={handleChange4}
            fullWidth
            variant="outlined"
          >
            {countries.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                {option.label}
              </MenuItem>
            ))}
          </CustomSelect>
        </Grid>
      </Grid>
    </>
    <>
      <Button
        variant="contained"
        color="error"
        sx={{
          mr: 1,
        }}
      >
        Cancel
      </Button>
      <Button variant="contained" color="primary">
        Submit
      </Button>
    </>
</div>
`}
      </CodeDialog>
    </>
  );
};

export default BasicHeaderFormCode;
