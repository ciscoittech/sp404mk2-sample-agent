// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import SimpleList from 'src/components/material-ui/lists/SimpleList';
import NestedList from 'src/components/material-ui/lists/NestedList';
import FolderList from 'src/components/material-ui/lists/FolderList';
import SelectedList from 'src/components/material-ui/lists/SelectedList';
import ControlsList from 'src/components/material-ui/lists/ControlsList';
import SwitchList from 'src/components/material-ui/lists/SwitchList';

import SimpleListCode from 'src/components/material-ui/lists/code/SimpleListCode';
import NestedListCode from 'src/components/material-ui/lists/code/NestedListCode';
import FolderListCode from 'src/components/material-ui/lists/code/FolderListCode';
import SelectedListCode from 'src/components/material-ui/lists/code/SelectedListCode';
import ControlsListCode from 'src/components/material-ui/lists/code/ControlsListCode';
import SwitchListCode from 'src/components/material-ui/lists/code/SwitchListCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'List',
  },
];

const MuiList = () => (
  <PageContainer title="List" description="this is List page">
    {/* breadcrumb */}
    <Breadcrumb title="List" items={BCrumb} />
    {/* end breadcrumb */}

    <ParentCard title="List">
      <Grid container spacing={3}>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Simple" codeModel={<SimpleListCode />}>
            <SimpleList />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Nested" codeModel={<NestedListCode />}>
            <NestedList />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Folder" codeModel={<FolderListCode />}>
            <FolderList />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Selected" codeModel={<SelectedListCode />}>
            <SelectedList />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Controls" codeModel={<ControlsListCode />}>
            <ControlsList />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Switch" codeModel={<SwitchListCode />}>
            <SwitchList />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>
);
export default MuiList;
