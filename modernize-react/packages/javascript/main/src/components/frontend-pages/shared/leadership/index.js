import React from 'react';
import { Box, Typography, Container } from '@mui/material';
import { Grid } from '@mui/material';
import 'slick-carousel/slick/slick.css';

import LeaderShipCarousel from './LeaderShipCarousel';
import Contact from './Contact';

const Leadership = () => {
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
          <Grid container spacing={3} alignItems="center" mb={6}>
            <Grid size={{ xs: 12, lg: 5, sm: 8 }}>
              <Typography
                variant="h4"
                mb={3}
                sx={{
                  fontSize: {
                    lg: '40px',
                    xs: '35px',
                  },
                }}
              >
                Our leadership
              </Typography>
              <Typography variant="body1" lineHeight="32px">
                Our robust analytics offer rich insights into the information buyers want, informing
                where teams
              </Typography>
            </Grid>
          </Grid>

          <LeaderShipCarousel />
        </Container>
      </Box>
      <Contact />
    </>
  );
};

export default Leadership;
