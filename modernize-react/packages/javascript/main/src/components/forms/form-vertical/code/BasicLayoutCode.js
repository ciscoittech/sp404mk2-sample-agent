import CodeDialog from '../../../shared/CodeDialog';
import React from 'react';
const BasicLayoutCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Grid } from '@mui/material';
import { InputAdornment, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import { TextField } from '@mui/material';
import { OutlinedInput } from '@mui/material';

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

<div>
    <Grid container>
        <Grid size={12} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-name" sx={{ mt: 0 }}>
            Name
          </CustomFormLabel>
        </Grid>
        <Grid size={12}>
          <CustomTextField id="bl-name" placeholder="John Deo" fullWidth />
        </Grid>
        <Grid size={12} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-company">
            Company
          </CustomFormLabel>
        </Grid>
        <Grid size={12}>
          <CustomTextField id="bl-company" placeholder="ACME Inc." fullWidth />
        </Grid>
        <Grid size={12} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-email">
            Email
          </CustomFormLabel>
        </Grid>
        <Grid size={12}>
          <CustomOutlinedInput
            endAdornment={<InputAdornment position="end">@example.com</InputAdornment>}
            id="bl-email"
            placeholder="john.deo"
            fullWidth
          />
        </Grid>
        <Grid size={12} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-phone">
            Phone No
          </CustomFormLabel>
        </Grid>
        <Grid size={12}>
          <CustomTextField id="bl-phone" placeholder="412 2150 451" fullWidth />
        </Grid>
        <Grid size={12} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-message">
            Message
          </CustomFormLabel>
        </Grid>
        <Grid size={12}>
          <CustomTextField
            id="bl-message"
            placeholder="Hi, Do you  have a moment to talk Jeo ?"
            multiline
            fullWidth
          />
        </Grid>
        <Grid size={12} mt={3}>
            <Button variant="contained" color="primary">Send</Button>
        </Grid>
    </Grid>
</div>
`}
      </CodeDialog>
    </>
  );
};

export default BasicLayoutCode;
