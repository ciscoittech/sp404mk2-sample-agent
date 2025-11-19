import React from 'react';
import { Grid } from '@mui/material';
// common component
import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../components/container/PageContainer';
import ParentCard from '../../components/shared/ParentCard';
import ChildCard from '../../components/shared/ChildCard';

// custom components
import ClickPopover from '../../components/material-ui/popover/ClickPopover';
import HoverPopover from '../../components/material-ui/popover/HoverPopover';

import ClickPopoverCode from '../../components/material-ui/popover/code/ClickPopoverCode';
import HoverPopoverCode from '../../components/material-ui/popover/code/HoverPopoverCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Popover',
  },
];

const MuiPopover = () => {
  return (
    // 2

    (<PageContainer title="Popover" description="this is Popover page">
      {/* breadcrumb */}
      <Breadcrumb title="Popover" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Popover">
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Click" codeModel={<ClickPopoverCode />}>
              <ClickPopover />
            </ChildCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Hover" codeModel={<HoverPopoverCode />}>
              <HoverPopover />
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>)
  );
};
export default MuiPopover;
