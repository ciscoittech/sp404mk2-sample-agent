import React from 'react';
import { Grid } from '@mui/material';
// common component
import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../components/container/PageContainer';
import ParentCard from '../../components/shared/ParentCard';
import ChildCard from '../../components/shared/ChildCard';

// custom components
import BasicTransferList from '../../components/material-ui/transfer-list/BasicTransferList';
import EnhancedTransferList from '../../components/material-ui/transfer-list/EnhancedTransferList';

import BasicTransferListCode from '../../components/material-ui/transfer-list/code/BasicTransferListCode';
import EnhancedTransferListCode from '../../components/material-ui/transfer-list/code/EnhancedTransferListCode';

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
  // 2

  (<PageContainer title="Transfer List" description="this is Transfer List page">
    {/* breadcrumb */}
    <Breadcrumb title="Transfer List" items={BCrumb} />
    {/* end breadcrumb */}
    <ParentCard title="Transfer List">
      <Grid container spacing={3}>
        <Grid size={12} display="flex" alignItems="stretch">
          <ChildCard title="Basic" codeModel={<BasicTransferListCode />}>
            <BasicTransferList />
          </ChildCard>
        </Grid>
        <Grid size={12} display="flex" alignItems="stretch">
          <ChildCard title="Enhanced" codeModel={<EnhancedTransferListCode />}>
            <EnhancedTransferList />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>)
);
export default MuiTransferList;
