// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import {
  FbOrdinaryForm,
  FbDefaultForm,
  FbBasicHeaderForm,
  FbReadonlyForm,
  FbDisabledForm,
  FbLeftIconForm,
  FbRightIconForm,
  FbInputVariants,
} from 'src/components/forms/form-layouts/index';
import PageContainer from 'src/components/container/PageContainer';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Form Layouts',
  },
];

const FormLayouts = () => (
  <PageContainer title="Form Layouts" description="this is innerpage">
    {/* breadcrumb */}
    <Breadcrumb title="Form Layouts" items={BCrumb} />
    {/* end breadcrumb */}

    <Grid container spacing={3}>
      <Grid
        size={{
          lg: 12,
          md: 12,
          xs: 12
        }}>
        <FbOrdinaryForm />
      </Grid>
      <Grid
        size={{
          lg: 12,
          md: 12,
          xs: 12
        }}>
        <FbInputVariants />
      </Grid>
      <Grid
        size={{
          lg: 12,
          md: 12,
          xs: 12
        }}>
        <FbDefaultForm />
      </Grid>
      <Grid
        size={{
          lg: 12,
          md: 12,
          xs: 12
        }}>
        <FbBasicHeaderForm />
      </Grid>
      <Grid
        size={{
          lg: 12,
          md: 12,
          xs: 12
        }}>
        <FbReadonlyForm />
      </Grid>
      <Grid
        size={{
          lg: 12,
          md: 12,
          xs: 12
        }}>
        <FbDisabledForm />
      </Grid>
      <Grid
        size={{
          lg: 6,
          md: 12,
          xs: 12
        }}>
        <FbLeftIconForm />
      </Grid>
      <Grid
        size={{
          lg: 6,
          md: 12,
          xs: 12
        }}>
        <FbRightIconForm />
      </Grid>
    </Grid>
  </PageContainer>
);

export default FormLayouts;
