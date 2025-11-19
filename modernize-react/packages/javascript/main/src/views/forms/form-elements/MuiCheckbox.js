import React from 'react';
import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';
import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';

import { Grid } from '@mui/material';

// custom components
import PositionCheckbox from '../../../components/forms/form-elements/checkbox/Position';
import SizesCheckbox from '../../../components/forms/form-elements/checkbox/Sizes';
import DefaultcolorsCheckbox from '../../../components/forms/form-elements/checkbox/DefaultColors';
import CustomEleCheckbox from '../../../components/forms/form-elements/checkbox/Custom';
import DefaultCheckbox from '../../../components/forms/form-elements/checkbox/Default';
import ColorsCheckbox from '../../../components/forms/form-elements/checkbox/Colors';

// codeModel
import CustomEleCheckboxCode from '../../../components/forms/form-elements/checkbox/code/CustomEleCheckboxCode';
import ColorsCheckboxCode from '../../../components/forms/form-elements/checkbox/code/ColorsCheckboxCode';
import DefaultCheckboxCode from '../../../components/forms/form-elements/checkbox/code/DefaultCheckboxCode';
import DefaultcolorsCheckboxCode from '../../../components/forms/form-elements/checkbox/code/DefaultcolorsCheckboxCode';
import SizesCheckboxCode from '../../../components/forms/form-elements/checkbox/code/SizesCheckboxCode';
import PositionCheckboxCode from '../../../components/forms/form-elements/checkbox/code/PositionCheckboxCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Checkbox',
  },
];

const ExCheckbox = () => {
  return (
    <PageContainer title="Checkbox" description="this is Checkbox page">
      {/* breadcrumb */}
      <Breadcrumb title="Checkbox" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Checkbox">
        <Grid container spacing={3}>
          {/* ------------------------------------------------------------------- */}
          {/* Custom  */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Custom" codeModel={<CustomEleCheckboxCode />}>
              <CustomEleCheckbox />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Colors  */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Colors" codeModel={<ColorsCheckboxCode />}>
              <ColorsCheckbox />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Default Checkbox */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Default" codeModel={<DefaultCheckboxCode />}>
              <DefaultCheckbox />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Default with colors */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Default with Colors" codeModel={<DefaultcolorsCheckboxCode />}>
              <DefaultcolorsCheckbox />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Sizes */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Sizes & Custom Icon" codeModel={<SizesCheckboxCode />}>
              <SizesCheckbox />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Position */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Position" codeModel={<PositionCheckboxCode />}>
              <PositionCheckbox />
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>
  );
};

export default ExCheckbox;
