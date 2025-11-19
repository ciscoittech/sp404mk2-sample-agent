// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import ClickPopover from 'src/components/material-ui/popover/ClickPopover';
import HoverPopover from 'src/components/material-ui/popover/HoverPopover';
import ClickPopoverCode from 'src/components/material-ui/popover/code/ClickPopoverCode';
import HoverPopoverCode from 'src/components/material-ui/popover/code/HoverPopoverCode';

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
    (<PageContainer title="Popover" description="this is Popover page">
      {/* breadcrumb */}
      <Breadcrumb title="Popover" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Popover">
        <Grid container spacing={3}>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              sm: 6
            }}>
            <ChildCard title="Click" codeModel={<ClickPopoverCode />}>
              <ClickPopover />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              sm: 6
            }}>
            <ChildCard title="Hover" codeModel={<HoverPopoverCode />}>
              <HoverPopover />
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>)
  );
}
export default MuiPopover;
