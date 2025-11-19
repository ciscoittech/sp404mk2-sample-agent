import React from 'react';
import { Box, Link, Typography, Tooltip } from '@mui/material';

import IconVisa from 'src/assets/images/frontend-pages/payments/icon-visa.svg';
import IconMasterCard from 'src/assets/images/frontend-pages/payments/icon-mastercard.svg';
import IconAmericanExpress from 'src/assets/images/frontend-pages/payments/icon-american-express.svg';
import IconDiscover from 'src/assets/images/frontend-pages/payments/icon-discover.svg';
import IconPaypal from 'src/assets/images/frontend-pages/payments/icon-paypal.svg';
import IcoMasetro from 'src/assets/images/frontend-pages/payments/icon-masetro.svg';
import IconJcb from 'src/assets/images/frontend-pages/payments/icon-jcb.svg';
import IconDiners from 'src/assets/images/frontend-pages/payments/icon-diners.svg';

const PaymentMethods = () => {
  return (
    <>
      <Typography textAlign="center" mt={6} variant="body1">
        Secured payment with PayPal & Razorpay
      </Typography>

      <Box
        display="flex"
        useflexgap="true"
        flexWrap="wrap"
        alignItems="center"
        justifyContent="center"
        mt={4}
        gap="56px"
      >
        <Link href="#">
          <Tooltip title="Visa">
            <img src={IconVisa} width={60} height={20} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="Mastercard">
            <img src={IconMasterCard} width={45} height={25} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="American express">
            <img src={IconAmericanExpress} width={80} height={34} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="Discover">
            <img src={IconDiscover} width={95} height={16} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="Paypal">
            <img src={IconPaypal} width={90} height={24} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="Maestro">
            <img src={IcoMasetro} width={45} height={28} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="JCB">
            <img src={IconJcb} width={31} height={24} alt="payment" />
          </Tooltip>
        </Link>
        <Link href="#">
          <Tooltip title="Diners">
            <img src={IconDiners} width={92} height={24} alt="payment" />
          </Tooltip>
        </Link>
      </Box>
    </>
  );
};

export default PaymentMethods;
