// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import * as React from 'react';

import { Box } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ProductTableList from 'src/components/apps/ecommerce/ProductTableList/ProductTableList';
import { ProductProvider } from 'src/context/EcommerceContext';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Search Table',
  },
];

const SearchTable = () => {
  return (
    <ProductProvider>
      <PageContainer title="Search Table" description="this is Search Table page">
        {/* breadcrumb */}
        <Breadcrumb title="Search Table" items={BCrumb} />
        {/* end breadcrumb */}
        <Box>
          <ProductTableList />
        </Box>
      </PageContainer>
    </ProductProvider>
  );
};

export default SearchTable;
