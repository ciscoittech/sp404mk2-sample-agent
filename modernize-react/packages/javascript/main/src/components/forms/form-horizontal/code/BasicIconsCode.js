import CodeDialog from '../../../shared/CodeDialog';

const BasicIconsCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Grid } from '@mui/material';
import { InputAdornment, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Typography } from '@mui/material';
import { OutlinedInput } from '@mui/material';
import { IconBuildingArch, IconMail, IconMessage2, IconPhone, IconUser } from '@tabler/icons';

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
    <Grid container spacing={3}>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-name" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Name
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconUser size="20" />
              </InputAdornment>
            }
            id="bi-name"
            placeholder="John Deo"
            fullWidth
          />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-company" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Company
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconBuildingArch size="20" />
              </InputAdornment>
            }
            id="bi-company"
            placeholder="ACME Inc."
            fullWidth
          />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-email" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Email
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconMail size="20" />
              </InputAdornment>
            }
            id="bi-email"
            placeholder="john.deo"
            fullWidth
          />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-phone" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Phone No
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            startAdornment={
              <InputAdornment position="start">
                <IconPhone size="20" />
              </InputAdornment>
            }
            id="bi-phone"
            placeholder="412 2150 451"
            fullWidth
          />
        </Grid>
        <Grid size={{xs: 12, sm: 3}} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-message" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Message
          </CustomFormLabel>
        </Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <CustomOutlinedInput
            id="bi-message"
            startAdornment={
              <InputAdornment position="start">
                <IconMessage2 size="20" />
              </InputAdornment>
            }
            placeholder="Hi, Do you  have a moment to talk Jeo ?"
            multiline
            fullWidth
          />
        </Grid>
        <Grid size={{xs: 12, sm: 3}}></Grid>
        <Grid size={{xs: 12, sm: 9}}>
          <Button variant="contained" color="primary">
            Send
          </Button>
        </Grid>
    </Grid>
</div>
`}
      </CodeDialog>
    </>
  );
};

export default BasicIconsCode;
