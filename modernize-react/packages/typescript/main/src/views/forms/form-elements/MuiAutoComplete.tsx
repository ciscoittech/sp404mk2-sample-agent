// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';

import ComboBoxAutocomplete from 'src/components/forms/form-elements/autoComplete/ComboBoxAutocomplete';
import CountrySelectAutocomplete from 'src/components/forms/form-elements/autoComplete/CountrySelectAutocomplete';
import ControlledStateAutocomplete from 'src/components/forms/form-elements/autoComplete/ControlledStateAutocomplete';
import FreeSoloAutocomplete from 'src/components/forms/form-elements/autoComplete/FreeSoloAutocomplete';
import MultipleValuesAutocomplete from 'src/components/forms/form-elements/autoComplete/MultipleValuesAutocomplete';
import CheckboxesAutocomplete from 'src/components/forms/form-elements/autoComplete/CheckboxesAutocomplete';
import SizesAutocomplete from 'src/components/forms/form-elements/autoComplete/SizesAutocomplete';

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';

// codeModel
import ComboBoxCode from 'src/components/forms/form-elements/autoComplete/code/ComboBoxCode';
import CountrySelectCode from 'src/components/forms/form-elements/autoComplete/code/CountrySelectCode';
import ControlledStateCode from 'src/components/forms/form-elements/autoComplete/code/ControlledStateCode';
import FreeSoloCode from 'src/components/forms/form-elements/autoComplete/code/FreeSoloCode';
import MultipleValuesCode from 'src/components/forms/form-elements/autoComplete/code/MultipleValuesCode';
import CheckboxesCode from 'src/components/forms/form-elements/autoComplete/code/CheckboxesCode';
import SizesCode from 'src/components/forms/form-elements/autoComplete/code/SizesCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'AutoComplete',
  },
];

const MuiAutoComplete = () => (
  <PageContainer title="Autocomplete" description="this is Autocomplete page">
    {/* breadcrumb */}
    <Breadcrumb title="AutoComplete" items={BCrumb} />
    {/* end breadcrumb */}

    <ParentCard title="Autocomplete">
      <Grid container spacing={3}>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Combo Box" codeModel={<ComboBoxCode />}>
            <ComboBoxAutocomplete />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Country Select" codeModel={<CountrySelectCode />}>
            <CountrySelectAutocomplete />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Controlled State" codeModel={<ControlledStateCode />}>
            <ControlledStateAutocomplete />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Free Solo" codeModel={<FreeSoloCode />}>
            <FreeSoloAutocomplete />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Multiple Values" codeModel={<MultipleValuesCode />}>
            <MultipleValuesAutocomplete />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Checkboxes" codeModel={<CheckboxesCode />}>
            <CheckboxesAutocomplete />
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            lg: 4,
            sm: 6
          }}>
          <ChildCard title="Sizes" codeModel={<SizesCode />}>
            <SizesAutocomplete />
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>
);
export default MuiAutoComplete;
