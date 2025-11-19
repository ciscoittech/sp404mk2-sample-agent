// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Box } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ProductChecout from 'src/components/apps/ecommerce/productCheckout/ProductCheckout';
import ChildCard from 'src/components/shared/ChildCard';
import { ProductProvider } from 'src/context/EcommerceContext';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Checkout',
  },
];

const EcommerceCheckout = () => {
  return (
    <ProductProvider>

      <PageContainer title="Checkout" description="this is Shop List page">
        {/* breadcrumb */}
        <Breadcrumb title="Checkout" items={BCrumb} />
        <ChildCard>
          {/* ------------------------------------------- */}
          {/* Right part */}
          {/* ------------------------------------------- */}
          <Box p={3} flexGrow={1}>
            <ProductChecout />
          </Box>
        </ChildCard>
      </PageContainer>
    </ProductProvider>
  );
};

export default EcommerceCheckout;
