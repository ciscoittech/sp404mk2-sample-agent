import React from 'react';
import { Grid } from '@mui/material';
// common component
import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../components/container/PageContainer';
import ParentCard from '../../components/shared/ParentCard';
import ChildCard from '../../components/shared/ChildCard';

// custom components
import SimpleList from '../../components/material-ui/lists/SimpleList';
import NestedList from '../../components/material-ui/lists/NestedList';
import FolderList from '../../components/material-ui/lists/FolderList';
import SelectedList from '../../components/material-ui/lists/SelectedList';
import ControlsList from '../../components/material-ui/lists/ControlsList';
import SwitchList from '../../components/material-ui/lists/SwitchList';

import SimpleListCode from '../../components/material-ui/lists/code/SimpleListCode';
import NestedListCode from '../../components/material-ui/lists/code/NestedListCode';
import FolderListCode from '../../components/material-ui/lists/code/FolderListCode';
import SelectedListCode from '../../components/material-ui/lists/code/SelectedListCode';
import ControlsListCode from '../../components/material-ui/lists/code/ControlsListCode';
import SwitchListCode from '../../components/material-ui/lists/code/SwitchListCode';

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
  // 2

  (<PageContainer title="List" description="this is List page">
    {/* breadcrumb */}
    <Breadcrumb title="List" items={BCrumb} />
    {/* end breadcrumb */}
    <ParentCard title="List">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Simple" codeModel={<SimpleListCode />}>
            <SimpleList />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Nested" codeModel={<NestedListCode />}>
            <NestedList />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Folder" codeModel={<FolderListCode />}>
            <FolderList />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Selected" codeModel={<SelectedListCode />}>
            <SelectedList />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Controls" codeModel={<ControlsListCode />}>
            <ControlsList />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Switch" codeModel={<SwitchListCode />}>
            <SwitchList />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>)
);
export default MuiList;
