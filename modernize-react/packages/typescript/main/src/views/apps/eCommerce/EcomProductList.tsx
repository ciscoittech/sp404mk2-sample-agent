// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ProductTableList from 'src/components/apps/ecommerce/ProductTableList/ProductTableList';
import BlankCard from 'src/components/shared/BlankCard';
import { ProductProvider } from 'src/context/EcommerceContext/index'

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Shop',
  },
];

const EcomProductList = () => {
  return (
    <ProductProvider>
      <PageContainer title="Shop List" description="this is Shop List page">
        {/* breadcrumb */}
        <Breadcrumb title="Ecom-Shop" items={BCrumb} />
        <BlankCard>
          {/* ------------------------------------------- */}
          {/* Left part */}
          {/* ------------------------------------------- */}
          <ProductTableList />
        </BlankCard>
      </PageContainer>
    </ProductProvider>
  );
};

export default EcomProductList;
