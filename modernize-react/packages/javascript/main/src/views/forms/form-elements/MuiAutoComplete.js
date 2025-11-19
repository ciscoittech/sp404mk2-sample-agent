import React from 'react';
import { Grid } from '@mui/material';

import ComboBoxAutocomplete from '../../../components/forms/form-elements/autoComplete/ComboBoxAutocomplete';
import CountrySelectAutocomplete from '../../../components/forms/form-elements/autoComplete/CountrySelectAutocomplete';
import ControlledStateAutocomplete from '../../../components/forms/form-elements/autoComplete/ControlledStateAutocomplete';
import FreeSoloAutocomplete from '../../../components/forms/form-elements/autoComplete/FreeSoloAutocomplete';
import MultipleValuesAutocomplete from '../../../components/forms/form-elements/autoComplete/MultipleValuesAutocomplete';
import CheckboxesAutocomplete from '../../../components/forms/form-elements/autoComplete/CheckboxesAutocomplete';
import SizesAutocomplete from '../../../components/forms/form-elements/autoComplete/SizesAutocomplete';

import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';
import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';

// codeModel
import ComboBoxCode from '../../../components/forms/form-elements/autoComplete/code/CheckboxesCode';
import CountrySelectCode from '../../../components/forms/form-elements/autoComplete/code/CountrySelectCode';
import ControlledStateCode from '../../../components/forms/form-elements/autoComplete/code/ControlledStateCode';
import FreeSoloCode from '../../../components/forms/form-elements/autoComplete/code/FreeSoloCode';
import MultipleValuesCode from '../../../components/forms/form-elements/autoComplete/code/MultipleValuesCode';
import CheckboxesCode from '../../../components/forms/form-elements/autoComplete/code/CheckboxesCode';
import SizesCode from '../../../components/forms/form-elements/autoComplete/code/SizesCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'AutoComplete',
  },
];

const ExAutoComplete = () => (
  // 2

  (<PageContainer title="Autocomplete" description="this is Autocomplete page">
    {/* breadcrumb */}
    <Breadcrumb title="AutoComplete" items={BCrumb} />
    {/* end breadcrumb */}
    <ParentCard title="Autocomplete">
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Combo Box" codeModel={<ComboBoxCode />}>
            <ComboBoxAutocomplete />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Country Select" codeModel={<CountrySelectCode />}>
            <CountrySelectAutocomplete />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Controlled State" codeModel={<ControlledStateCode />}>
            <ControlledStateAutocomplete />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Free Solo" codeModel={<FreeSoloCode />}>
            <FreeSoloAutocomplete />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Multiple Values" codeModel={<MultipleValuesCode />}>
            <MultipleValuesAutocomplete />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Checkboxes" codeModel={<CheckboxesCode />}>
            <CheckboxesAutocomplete />
          </ChildCard>
        </Grid>
        <Grid size={{ xs: 12, lg: 4, sm: 6 }} display="flex" alignItems="stretch">
          <ChildCard title="Sizes" codeModel={<SizesCode />}>
            <SizesAutocomplete />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>)
);
export default ExAutoComplete;
