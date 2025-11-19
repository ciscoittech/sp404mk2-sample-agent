import React from 'react';
import { Typography } from '@mui/material';

import LogoIcon from 'src/assets/images/logos/logoIcon.svg';

const ContentArea = () => {
  return (
    <>
      <Typography
        variant="h4"
        lineHeight={1.4}
        mb={3}
        fontWeight={700}
        sx={{
          fontSize: {
            lg: '40px',
            xs: '35px',
          },
          mr: {
            xs: 0,
            lg: 4,
          },
        }}
      >
        What our clients think{' '}
        <img
          src={LogoIcon}
          alt="logo"
          width={40}
          height={40}
          style={{ margin: '0 8px', verticalAlign: 'middle' }}
        />{' '}
        about us?
      </Typography>
      <Typography variant="body1" lineHeight={1.8}>
        Our users' feedback is a testament to our commitment to quality and user satisfaction. Read
        what they have to say about their journey with us.
      </Typography>
    </>
  );
};

export default ContentArea;
