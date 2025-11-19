// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import BasicTransferList from 'src/components/material-ui/transfer-list/BasicTransferList';
import EnhancedTransferList from 'src/components/material-ui/transfer-list/EnhancedTransferList';

import BasicTransferListCode from 'src/components/material-ui/transfer-list/code/BasicTransferListCode';
import EnhancedTransferListCode from 'src/components/material-ui/transfer-list/code/EnhancedTransferListCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Transfer List',
  },
];

const MuiTransferList = () => (
  <PageContainer title="Transfer List" description="this is Transfer List page">
    {/* breadcrumb */}
    <Breadcrumb title="Transfer List" items={BCrumb} />
    {/* end breadcrumb */}

    <ParentCard title="Transfer List">
      <Grid container spacing={3}>
        <Grid display="flex" alignItems="stretch" size={12}>
          <ChildCard title="Basic" codeModel={<BasicTransferListCode />}>
            <BasicTransferList />
          </ChildCard>
        </Grid>
        <Grid display="flex" alignItems="stretch" size={12}>
          <ChildCard title="Enhanced" codeModel={<EnhancedTransferListCode />}>
            <EnhancedTransferList />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>
);
export default MuiTransferList;
