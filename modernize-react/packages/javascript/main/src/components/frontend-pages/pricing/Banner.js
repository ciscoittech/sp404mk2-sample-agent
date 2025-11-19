import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import { Grid } from '@mui/material';

const Banner = () => {
  return (
    <>
      <Box
        bgcolor="primary.light"
        sx={{
          paddingTop: {
            xs: '40px',
            lg: '100px',
          },
          paddingBottom: {
            xs: '40px',
            lg: '100px',
          },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3} justifyContent="center">
            <Grid size={{ xs: 12, lg: 8 }} alignItems="center" textAlign="center">
              <Typography color="primary.main" textTransform="uppercase" fontSize="13px">
                Pricing Page
              </Typography>
              <Typography
                variant="h1"
                mb={3}
                lineHeight={1.4}
                fontWeight={700}
                sx={{
                  fontSize: {
                    xs: '34px',
                    sm: '48px',
                    lg: '56px',
                  },
                }}
              >
                Choose Your Plan
              </Typography>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </>
  );
};

export default Banner;
