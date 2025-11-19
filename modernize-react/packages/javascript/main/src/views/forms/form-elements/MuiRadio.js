import React from 'react';
import { Grid } from '@mui/material';
import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';
import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';

// custom
import ColorLabelRadio from "../../../components/forms/form-elements/radio/ColorLabel";
import DefaultRadio from "../../../components/forms/form-elements/radio/Default";
import ColorsRadio from "../../../components/forms/form-elements/radio/Colors";
import SizesRadio from "../../../components/forms/form-elements/radio/Sizes";
import CustomExRadio from "../../../components/forms/form-elements/radio/Custom";
import PositionRadio from "../../../components/forms/form-elements/radio/Position";

// codeModel
import CustomExRadioCode from '../../../components/forms/form-elements/radio/code/CustomExRadioCode';
import ColorLabelRadioCode from '../../../components/forms/form-elements/radio/code/ColorLabelRadioCode';
import DefaultRadioCode from '../../../components/forms/form-elements/radio/code/DefaultRadioCode';
import ColorsRadioCode from '../../../components/forms/form-elements/radio/code/ColorsRadioCode';
import SizesRadioCode from '../../../components/forms/form-elements/radio/code/SizesRadioCode';
import PositionRadioCode from '../../../components/forms/form-elements/radio/code/PositionRadioCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Radio',
  },
];

const ExRadio = () => {

  return (
    <PageContainer title="Radio" description="this is Radio page">
      {/* breadcrumb */}
      <Breadcrumb title="Radio" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Radio">
        <Grid container spacing={3}>
          {/* ------------------------------------------------------------------- */}
          {/* Custom */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Custom" codeModel={<CustomExRadioCode />}>
              <CustomExRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Color with label */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Color with Label" codeModel={<ColorLabelRadioCode />}>
              <ColorLabelRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Default */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Default" codeModel={<DefaultRadioCode />}>
              <DefaultRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Default Colors */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Default Colors" codeModel={<ColorsRadioCode />}>
              <ColorsRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Sizes */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Sizes" codeModel={<SizesRadioCode />}>
              <SizesRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Position */}
          {/* ------------------------------------------------------------------- */}
          <Grid size={{ xs: 12, lg: 6, sm: 6 }} display="flex" alignItems="stretch">
            <ChildCard title="Position" codeModel={<PositionRadioCode />}>
              <PositionRadio />
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>
  );
};

export default ExRadio;
