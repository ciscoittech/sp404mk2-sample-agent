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
} from '../../components/forms/form-layouts/index';
import PageContainer from '../../components/container/PageContainer';
import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';

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
      <Grid size={12}>
        <FbOrdinaryForm />
      </Grid>
      <Grid size={12}>
        <FbInputVariants />
      </Grid>
      <Grid size={12}>
        <FbDefaultForm />
      </Grid>
      <Grid size={12}>
        <FbBasicHeaderForm />
      </Grid>
      <Grid size={12}>
        <FbReadonlyForm />
      </Grid>
      <Grid size={12}>
        <FbDisabledForm />
      </Grid>
      <Grid size={{ xs: 12, lg: 6 }}>
        <FbLeftIconForm />
      </Grid>
      <Grid size={{ xs: 12, lg: 6 }}>
        <FbRightIconForm />
      </Grid>
    </Grid>
  </PageContainer>
);

export default FormLayouts;
