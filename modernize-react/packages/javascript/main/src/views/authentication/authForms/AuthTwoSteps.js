import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { Link } from 'react-router';

import CustomTextField from '../../../components/forms/theme-elements/CustomTextField';
import CustomFormLabel from '../../../components/forms/theme-elements/CustomFormLabel';
import { Stack } from '@mui/system';


const AuthTwoSteps = () => (
    <>



        <Box mt={4} >
            <Stack mb={3}>
                <CustomFormLabel htmlFor="code">Type your 6 digits security code </CustomFormLabel>
                <Stack spacing={2} direction="row">
                    <CustomTextField id="code" variant="outlined" fullWidth />
                    <CustomTextField id="code" variant="outlined" fullWidth />
                    <CustomTextField id="code" variant="outlined" fullWidth />
                    <CustomTextField id="code" variant="outlined" fullWidth />
                    <CustomTextField id="code" variant="outlined" fullWidth />
                    <CustomTextField id="code" variant="outlined" fullWidth />
                </Stack>

            </Stack>
            <Button
                color="primary"
                variant="contained"
                size="large"
                fullWidth
                component={Link}
                to="/">
                Verify My Account
            </Button>



            <Stack direction="row" spacing={1} mt={3}>
                <Typography
                    color="textSecondary"
                    variant="h6"
                    fontWeight="400"
                >
                    Didn't get the code?
                </Typography>
                <Typography
                    component={Link}
                    to="/"
                    fontWeight="500"
                    sx={{
                        textDecoration: 'none',
                        color: 'primary.main',
                    }}
                >
                    Resend
                </Typography>
            </Stack>
        </Box>
    </>
);

export default AuthTwoSteps;
