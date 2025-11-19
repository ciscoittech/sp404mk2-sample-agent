import React from 'react';
import { Box, Container } from '@mui/material';
import ContentArea from './ContentArea';
import ReviewCarousel from './ReviewCarousel';
import { Grid } from '@mui/material';

const Reviews = () => {
  return (
    <>
      <Box
        sx={{
          py: {
            xs: 5,
            lg: 10,
          },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3} alignItems="center" justifyContent="space-between">
            <Grid size={{ xs: 12, lg: 5, sm: 8 }} pr={6}>
              <ContentArea />
            </Grid>
            <Grid size={{ xs: 12, lg: 6 }}>
              <Grid container spacing={3} justifyContent="center">
                <Grid size={{ xs: 12, lg: 10 }}>
                  <ReviewCarousel />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </>
  );
};

export default Reviews;
