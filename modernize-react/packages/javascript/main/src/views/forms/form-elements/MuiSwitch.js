import React from 'react';
import { Grid } from '@mui/material';

import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';
import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';

import CustomExSwitch from '../../../components/forms/form-elements/switch/Custom';
import DefaultSwitch from '../../../components/forms/form-elements/switch/Default';
import DefaultLabelSwitch from '../../../components/forms/form-elements/switch/DefaultLabel';
import SizesSwitch from '../../../components/forms/form-elements/switch/Sizes';
import ColorsSwitch from '../../../components/forms/form-elements/switch/Colors';
import PositionSwitch from '../../../components/forms/form-elements/switch/Position';

import CustomSwitchCode from '../../../components/forms/form-elements/switch/code/CustomSwitchCode';
import DefaultSwitchCode from '../../../components/forms/form-elements/switch/code/DefaultSwitchCode';
import DefaultLabelSwitchCode from '../../../components/forms/form-elements/switch/code/DefaultLabelSwitchCode';
import SizesSwitchCode from '../../../components/forms/form-elements/switch/code/SizesSwitchCode';
import ColorsSwitchCode from '../../../components/forms/form-elements/switch/code/ColorsSwitchCode';
import PositionSwitchCode from '../../../components/forms/form-elements/switch/code/PositionSwitchCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Switch',
  },
];

const ExSwitch = () => (
  // 2
  (<PageContainer title="Switch" description="this is Switch page">
    {/* breadcrumb */}
    <Breadcrumb title="Switch" items={BCrumb} />
    {/* end breadcrumb */}
    <ParentCard title="Switch">
      <Grid container spacing={3}>
        {/* ------------------------------------------------------------------- */}
        {/* Custom */}
        {/* ------------------------------------------------------------------- */}
        <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Custom" codeModel={<CustomSwitchCode />}>
            <CustomExSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Default */}
        {/* ------------------------------------------------------------------- */}
        <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Default" codeModel={<DefaultSwitchCode />}>
            <DefaultSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Default with label */}
        {/* ------------------------------------------------------------------- */}
        <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Default with Label" codeModel={<DefaultLabelSwitchCode />}>
            <DefaultLabelSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Sizes */}
        {/* ------------------------------------------------------------------- */}
        <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Sizes" codeModel={<SizesSwitchCode />}>
            <SizesSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Default Colors */}
        {/* ------------------------------------------------------------------- */}
        <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Default Colors" codeModel={<ColorsSwitchCode />}>
            <ColorsSwitch />
          </ChildCard>
        </Grid>
        {/* ------------------------------------------------------------------- */}
        {/* Placement */}
        {/* ------------------------------------------------------------------- */}
        <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Placement" codeModel={<PositionSwitchCode />}>
            <PositionSwitch />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>)
);
export default ExSwitch;
