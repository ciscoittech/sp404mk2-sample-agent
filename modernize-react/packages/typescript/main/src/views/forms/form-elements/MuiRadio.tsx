// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ColorLabelRadio from "src/components/forms/form-elements/radio/ColorLabel";
import DefaultRadio from "src/components/forms/form-elements/radio/Default";
import ColorsRadio from "src/components/forms/form-elements/radio/Colors";
import SizesRadio from "src/components/forms/form-elements/radio/Sizes";
import CustomExRadio from "src/components/forms/form-elements/radio/Custom";
import PositionRadio from "src/components/forms/form-elements/radio/Position";

// codeModel
import CustomExRadioCode from 'src/components/forms/form-elements/radio/code/CustomExRadioCode';
import ColorLabelRadioCode from 'src/components/forms/form-elements/radio/code/ColorLabelRadioCode';
import DefaultRadioCode from 'src/components/forms/form-elements/radio/code/DefaultRadioCode';
import ColorsRadioCode from 'src/components/forms/form-elements/radio/code/ColorsRadioCode';
import SizesRadioCode from 'src/components/forms/form-elements/radio/code/SizesRadioCode';
import PositionRadioCode from 'src/components/forms/form-elements/radio/code/PositionRadioCode';

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
    (<PageContainer title="Radio" description="this is Radio page">
      {/* breadcrumb */}
      <Breadcrumb title="Radio" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Radio">
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
            <ChildCard title="Custom" codeModel={<CustomExRadioCode />}>
              <CustomExRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Color with label */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 6,
              sm: 6
            }}>
            <ChildCard title="Color with Label" codeModel={<ColorLabelRadioCode />}>
              <ColorLabelRadio />
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
            <ChildCard title="Default" codeModel={<DefaultRadioCode />}>
              <DefaultRadio />
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
            <ChildCard title="Default Colors" codeModel={<ColorsRadioCode />}>
              <ColorsRadio />
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
            <ChildCard title="Sizes" codeModel={<SizesRadioCode />}>
              <SizesRadio />
            </ChildCard>
          </Grid>
          {/* ------------------------------------------------------------------- */}
          {/* Position */}
          {/* ------------------------------------------------------------------- */}
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 6,
              sm: 6
            }}>
            <ChildCard title="Position" codeModel={<PositionRadioCode />}>
              <PositionRadio />
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>)
  );
};

export default ExRadio;
