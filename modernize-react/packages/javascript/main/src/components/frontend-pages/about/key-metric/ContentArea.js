import React from 'react';
import { Typography } from '@mui/material';

const ContentArea = () => {
  return (
    <>
      <Typography
        variant="h1"
        mb={2}
        lineHeight={1.4}
        fontWeight={700}
        sx={{
          fontSize: {
            xs: '34px',
            sm: '40px',
          },
        }}
      >
        Key metric at a glance
      </Typography>
      <Typography lineHeight={1.9}>
        From the year we were founded to the impressive customer base we've built, and the growth
        percentages that reflect our continuous improvement, these numbers tell our story at a
        glance. Explore the data that drives our mission and underscores our commitment to
        excellence.
      </Typography>
    </>
  );
};

export default ContentArea;
