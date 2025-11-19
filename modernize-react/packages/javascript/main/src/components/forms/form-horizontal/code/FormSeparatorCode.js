import CodeDialog from '../../../shared/CodeDialog';
import React from 'react';
const FormSeparatorCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import {
  InputAdornment,
  Button,
  Typography,
  Divider,
  MenuItem,
  IconButton,
  Stack,
} from '@mui/material';
import { Grid } from '@mui/material';
import { IconEye, IconEyeOff } from '@tabler/icons';
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import { TextField } from '@mui/material';
import { OutlinedInput } from '@mui/material';
import { Select } from '@mui/material';

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

const CustomOutlinedInput = styled((props) => <OutlinedInput {...props} />)(({ theme }) => ({
  '& .MuiOutlinedInput-input::-webkit-input-placeholder': {
    color: theme.palette.text.secondary,
    opacity: '0.8',
  },

  '& .MuiTypography-root': {
    color: theme.palette.text.secondary,
  },

  '& .MuiOutlinedInput-input.Mui-disabled::-webkit-input-placeholder': {
    color: theme.palette.text.secondary,
    opacity: '1',
  },
}));

const CustomSelect = styled((props) => <Select {...props} />)(({}) => ({}));

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

const [country, setCountry] = React.useState('');

  const handleChange = (event) => {
    setCountry(event.target.value);
  };

  const [showPassword, setShowPassword] = React.useState(false);

  const handleClickShowPassword = () => setShowPassword((show) => !show);

  const handleMouseDownPassword = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
};

<div>
    <Typography variant="h6" mb={3}>
        Account Details
    </Typography>
    <Grid container spacing={3}>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-uname" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Username
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomTextField id="fs-uname" placeholder="John Deo" fullWidth />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-email" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Email
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            endAdornment={<InputAdornment position="end">@example.com</InputAdornment>}
            id="fs-email"
            placeholder="john.deo"
            fullWidth
          />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-pwd" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Password
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            type={showPassword ? 'text' : 'password'}
            endAdornment={
              <InputAdornment position="end">
                <IconButton
                  aria-label="toggle password visibility"
                  onClick={handleClickShowPassword}
                  onMouseDown={handleMouseDownPassword}
                  edge="end"
                >
                  {showPassword ? <IconEyeOff size="20" /> : <IconEye size="20" />}
                </IconButton>
              </InputAdornment>
            }
            id="fs-pwd"
            placeholder="john.deo"
            fullWidth
          />
        </Grid>
        <Grid size={12}>
          <Divider sx={{mx: "-24px"}} />
          <Typography variant="h6" mt={2}>
            Personal Info
          </Typography>
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-fname" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Full Name
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomTextField id="fs-fname" placeholder="John Deo" fullWidth />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-country" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Country
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomSelect
            id="standard-select-currency"
            value={country}
            onChange={handleChange}
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
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-date" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Birth Date
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomTextField type="date" id="fs-date" placeholder="John Deo" fullWidth />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="fs-phone" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Phone no
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomTextField id="fs-phone" placeholder="123 4567 201" fullWidth />
        </Grid>
        <Grid size={{xs: 12, sm: 3}}></Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <Stack direction="row" spacing={2}>
            <Button variant="contained" color="primary">
              Submit
            </Button>
            <Button variant="text" color="error">
              Cancel
            </Button>
          </Stack>
        </Grid>
    </Grid>
</div>
`}
      </CodeDialog>
    </>
  );
};

export default FormSeparatorCode;
