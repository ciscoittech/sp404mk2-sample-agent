import React from 'react';
import { Grid } from '@mui/material';
import InputAdornment from '@mui/material/InputAdornment';
import Button from '@mui/material/Button';
import CustomFormLabel from '../theme-elements/CustomFormLabel';
import CustomTextField from '../theme-elements/CustomTextField';
import CustomOutlinedInput from '../theme-elements/CustomOutlinedInput';

const BasicLayout = () => {
  return (
    <div>
      {/* ------------------------------------------------------------------------------------------------ */}
      {/* Basic Layout */}
      {/* ------------------------------------------------------------------------------------------------ */}
      <Grid container spacing={3}>
        {/* 1 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-name" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Name
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
          <CustomTextField id="bl-name" placeholder="John Deo" fullWidth />
        </Grid>
        {/* 2 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-company" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Company
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
          <CustomTextField id="bl-company" placeholder="ACME Inc." fullWidth />
        </Grid>
        {/* 3 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-email" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Email
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
          <CustomOutlinedInput
            endAdornment={<InputAdornment position="end">@example.com</InputAdornment>}
            id="bl-email"
            placeholder="john.deo"
            fullWidth
          />
        </Grid>
        {/* 4 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-phone" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Phone No
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
          <CustomTextField id="bl-phone" placeholder="412 2150 451" fullWidth />
        </Grid>
        {/* 5 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bl-message" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Message
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
          <CustomTextField
            id="bl-message"
            placeholder="Hi, Do you  have a moment to talk Jeo ?"
            multiline
            fullWidth
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 3 }}></Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
          <Button variant="contained" color="primary">
            Send
          </Button>
        </Grid>
      </Grid>
    </div>
  );
};

export default BasicLayout;
