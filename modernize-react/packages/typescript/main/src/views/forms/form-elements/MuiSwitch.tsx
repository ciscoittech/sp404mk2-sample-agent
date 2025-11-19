// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import CustomExSwitch from 'src/components/forms/form-elements/switch/Custom';
import DefaultSwitch from 'src/components/forms/form-elements/switch/Default';
import DefaultLabelSwitch from 'src/components/forms/form-elements/switch/DefaultLabel';
import SizesSwitch from 'src/components/forms/form-elements/switch/Sizes';
import ColorsSwitch from 'src/components/forms/form-elements/switch/Colors';
import PositionSwitch from 'src/components/forms/form-elements/switch/Position';

import CustomSwitchCode from 'src/components/forms/form-elements/switch/code/ColorsSwitchCode';
import DefaultSwitchCode from 'src/components/forms/form-elements/switch/code/DefaultSwitchCode';
import DefaultLabelSwitchCode from 'src/components/forms/form-elements/switch/code/DefaultLabelSwitchCode';
import SizesSwitchCode from 'src/components/forms/form-elements/switch/code/SizesSwitchCode';
import ColorsSwitchCode from 'src/components/forms/form-elements/switch/code/ColorsSwitchCode';
import PositionSwitchCode from 'src/components/forms/form-elements/switch/code/PositionSwitchCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Switch',
  },
];

const MuiSwitch = () => (
  <PageContainer title="Switch" description="this is Switch page">
    {/* breadcrumb */}
    <Breadcrumb title="Switch" items={BCrumb} />
    {/* end breadcrumb */}
    <ParentCard title="Switch">
      <Grid container spacing={3}>
        {/* ------------------------------------------------------------------- */}
        {/* Custom */}
        {/* ------------------------------------------------------------------- */}
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 6,
            sm: 6
          }}>
          <ChildCard title="Custom" codeModel={<CustomSwitchCode />}>
            <CustomExSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Default */}
        {/* ------------------------------------------------------------------- */}
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 6,
            sm: 6
          }}>
          <ChildCard title="Default" codeModel={<DefaultSwitchCode />}>
            <DefaultSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Default with label */}
        {/* ------------------------------------------------------------------- */}
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 6,
            sm: 6
          }}>
          <ChildCard title="Default with Label" codeModel={<DefaultLabelSwitchCode />}>
            <DefaultLabelSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Sizes */}
        {/* ------------------------------------------------------------------- */}
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 6,
            sm: 6
          }}>
          <ChildCard title="Sizes" codeModel={<SizesSwitchCode />}>
            <SizesSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Default Colors */}
        {/* ------------------------------------------------------------------- */}
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 6,
            sm: 6
          }}>
          <ChildCard title="Default Colors" codeModel={<ColorsSwitchCode />}>
            <ColorsSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Placement */}
        {/* ------------------------------------------------------------------- */}
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 6,
            sm: 6
          }}>
          <ChildCard title="Placement" codeModel={<PositionSwitchCode />}>
            <PositionSwitch />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>
);
export default MuiSwitch;
