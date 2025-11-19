import { Grid } from '@mui/material';
import InputAdornment from '@mui/material/InputAdornment';
import Button from '@mui/material/Button';
import React from 'react';
import CustomFormLabel from '../theme-elements/CustomFormLabel';
import CustomOutlinedInput from '../theme-elements/CustomOutlinedInput';
import { IconBuildingArch, IconMail, IconMessage2, IconPhone, IconUser } from '@tabler/icons';

const BasicIcons = () => {
  return (
    <div>
      {/* ------------------------------------------------------------------------------------------------ */}
      {/* Basic Layout */}
      {/* ------------------------------------------------------------------------------------------------ */}
      <Grid container spacing={3}>
        {/* 1 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-name" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Name
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
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
        {/* 2 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-company" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Company
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
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
        {/* 3 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-email" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Email
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
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
        {/* 4 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-phone" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Phone No
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
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
        {/* 5 */}
        <Grid size={{ xs: 12, sm: 3 }} display="flex" alignItems="center">
          <CustomFormLabel htmlFor="bi-message" sx={{ mt: 0, mb: { xs: '-10px', sm: 0 } }}>
            Message
          </CustomFormLabel>
        </Grid>
        <Grid size={{ xs: 12, sm: 9 }}>
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

export default BasicIcons;
