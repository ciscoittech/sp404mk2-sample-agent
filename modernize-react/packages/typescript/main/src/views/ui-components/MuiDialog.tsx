// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import SimpleDialog from 'src/components/material-ui/dialog/SimpleDialog';
import AlertDialog from 'src/components/material-ui/dialog/AlertDialog';
import TransitionDialog from 'src/components/material-ui/dialog/TransitionDialog';
import FormDialog from 'src/components/material-ui/dialog/FormDialog';
import FullscreenDialog from 'src/components/material-ui/dialog/FullscreenDialog';
import MaxWidthDialog from 'src/components/material-ui/dialog/MaxWidthDialog';
import ScrollContentDialog from 'src/components/material-ui/dialog/ScrollContentDialog';
import ResponsiveDialog from 'src/components/material-ui/dialog/ResponsiveDialog';

import SimpleCode from 'src/components/material-ui/dialog/code/SimpleCode';
import AlertCode from 'src/components/material-ui/dialog/code/AlertCode';
import TransitionCode from 'src/components/material-ui/dialog/code/TransitionCode';
import FormCode from 'src/components/material-ui/dialog/code/FormCode';
import FullScreenCode from 'src/components/material-ui/dialog/code/FullScreenCode';
import MaxWidthCode from 'src/components/material-ui/dialog/code/MaxWidthCode';
import ScrollingContentCode from 'src/components/material-ui/dialog/code/ScrollingContentCode';
import ResponsiveFullscreenCode from 'src/components/material-ui/dialog/code/ResponsiveFullscreenCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Dialog',
  },
];

const MuiDialog = () => (
  <PageContainer title="Dialog" description="this is Dialog page">
    {/* breadcrumb */}
    <Breadcrumb title="Dialog" items={BCrumb} />
    {/* end breadcrumb */}

    <ParentCard title="Dialog">
      <Grid container spacing={3}>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Simple" codeModel={<SimpleCode />}>
            <SimpleDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Alert" codeModel={<AlertCode />}>
            <AlertDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Transition" codeModel={<TransitionCode />}>
            <TransitionDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Form" codeModel={<FormCode />}>
            <FormDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Full screen" codeModel={<FullScreenCode />}>
            <FullscreenDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Max width" codeModel={<MaxWidthCode />}>
            <MaxWidthDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Scrolling Content" codeModel={<ScrollingContentCode />}>
            <ScrollContentDialog />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Responsive Fullscreen" codeModel={<ResponsiveFullscreenCode />}>
            <ResponsiveDialog />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>
);
export default MuiDialog;
