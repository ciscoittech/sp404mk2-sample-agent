import React from 'react';
import { Grid } from '@mui/material';
import Breadcrumb from '../../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../../components/container/PageContainer';
import ParentCard from '../../../components/shared/ParentCard';
import ChildCard from '../../../components/shared/ChildCard';

import DefaultButtons from '../../../components/forms/form-elements/button/DefaultButtons';
import ColorButtons from '../../../components/forms/form-elements/button/ColorButtons';
import IconLoadingButtons from '../../../components/forms/form-elements/button/IconLoadingButtons';
import SizeButton from '../../../components/forms/form-elements/button/SizeButton';

import OutlinedDefaultButtons from '../../../components/forms/form-elements/button/OutlinedDefaultButtons';
import OutlinedIconButtons from '../../../components/forms/form-elements/button/OutlinedIconButtons';
import OutlinedSizeButton from '../../../components/forms/form-elements/button/OutlinedSizeButton';

import TextDefaultButtons from '../../../components/forms/form-elements/button/TextDefaultButtons';
import TextColorButtons from '../../../components/forms/form-elements/button/TextColorButtons';
import TextIconButtons from '../../../components/forms/form-elements/button/TextIconButtons';
import TextSizeButton from '../../../components/forms/form-elements/button/TextSizeButton';

import IconColorButtons from '../../../components/forms/form-elements/button/IconColorButtons';
import IconSizeButtons from '../../../components/forms/form-elements/button/IconSizeButtons';

import FabDefaultButton from '../../../components/forms/form-elements/button/FabDefaultButton';
import FabColorButtons from '../../../components/forms/form-elements/button/FabColorButtons';
import FabSizeButtons from '../../../components/forms/form-elements/button/FabSizeButtons';

import DefaultButtonGroup from '../../../components/forms/form-elements/button/DefaultButtonGroup';
import SizeButtonGroup from '../../../components/forms/form-elements/button/SizeButtonGroup';
import VerticalButtonGroup from '../../../components/forms/form-elements/button/VerticalButtonGroup';
import ColorButtonGroup from '../../../components/forms/form-elements/button/ColorButtonGroup';
import TextButtonGroup from '../../../components/forms/form-elements/button/TextButtonGroup';

// codeModel
import DefaultCode from '../../../components/forms/form-elements/button/code/DefaultCode';
import ColorsCode from '../../../components/forms/form-elements/button/code/ColorsCode';
import LoadingButtonsCode from '../../../components/forms/form-elements/button/code/LoadingButtonsCode';
import SizesCode from '../../../components/forms/form-elements/button/code/SizesCode';
import OutlinedCode from '../../../components/forms/form-elements/button/code/OutlinedCode';
import OutlinedIconCode from '../../../components/forms/form-elements/button/code/OutlinedIconCode';
import OutlineSizeCode from '../../../components/forms/form-elements/button/code/OutlineSizeCode';
import TextCode from '../../../components/forms/form-elements/button/code/TextCode';
import TextColorCode from '../../../components/forms/form-elements/button/code/TextColorCode';
import TextIconColor from '../../../components/forms/form-elements/button/code/TextIconColor';
import TextSizesCode from '../../../components/forms/form-elements/button/code/TextSizesCode';
import IconColorCode from '../../../components/forms/form-elements/button/code/IconColorCode';
import IconSizesCode from '../../../components/forms/form-elements/button/code/IconSizesCode';
import FABCode from '../../../components/forms/form-elements/button/code/FABCode';
import FABColorCode from '../../../components/forms/form-elements/button/code/FABColorCode';
import FABSizeCode from '../../../components/forms/form-elements/button/code/FABSizeCode';
import DefaultButtonGroupCode from '../../../components/forms/form-elements/button/code/DefaultButtonGroupCode';
import SizeButtonGroupCode from '../../../components/forms/form-elements/button/code/SizeButtonGroupCode';
import VerticalButtonGroupCode from '../../../components/forms/form-elements/button/code/VerticalButtonGroupCode';
import TextButtonGroupCode from '../../../components/forms/form-elements/button/code/TextButtonGroupCode';
import ColorButtonGroupCode from '../../../components/forms/form-elements/button/code/ColorButtonGroupCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Button',
  },
];

const ExButton = () => (
  // 2

  (<PageContainer title="Buttons" description="this is Buttons page">
    {/* breadcrumb */}
    <Breadcrumb title="Button" items={BCrumb} />
    {/* end breadcrumb */}
    <Grid container spacing={3}>
      <Grid size={12}>
        <ParentCard title="Buttons">
          <Grid container spacing={3}>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Default" codeModel={<DefaultCode />}>
                <DefaultButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Colors" codeModel={<ColorsCode />}>
                <ColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Loading Buttons" codeModel={<LoadingButtonsCode />}>
                <IconLoadingButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Sizes" codeModel={<SizesCode />}>
                <SizeButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Outlined" codeModel={<OutlinedCode />}>
                <OutlinedDefaultButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Outlined Icon" codeModel={<OutlinedIconCode />}>
                <OutlinedIconButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Outline Size" codeModel={<OutlineSizeCode />}>
                <OutlinedSizeButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Text" codeModel={<TextCode />}>
                <TextDefaultButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Text Color" codeModel={<TextColorCode />}>
                <TextColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Text Icon" codeModel={<TextIconColor />}>
                <TextIconButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Text Sizes" codeModel={<TextSizesCode />}>
                <TextSizeButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Icon Color" codeModel={<IconColorCode />}>
                <IconColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Icon Sizes" codeModel={<IconSizesCode />}>
                <IconSizeButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="FAB" codeModel={<FABCode />}>
                <FabDefaultButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="FAB Color" codeModel={<FABColorCode />}>
                <FabColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="FAB Size" codeModel={<FABSizeCode />}>
                <FabSizeButtons />
              </ChildCard>
            </Grid>
          </Grid>
        </ParentCard>
      </Grid>
      <Grid size={12}>
        <ParentCard title="Button Group">
          <Grid container spacing={3}>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Default" codeModel={<DefaultButtonGroupCode />}>
                <DefaultButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Sizes" codeModel={<SizeButtonGroupCode />}>
                <SizeButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Verical" codeModel={<VerticalButtonGroupCode />}>
                <VerticalButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={{ xs: 12, lg: 6 }} display="flex" alignItems="stretch">
              <ChildCard title="Text" codeModel={<TextButtonGroupCode />}>
                <TextButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid size={12} display="flex" alignItems="stretch">
              <ChildCard title="Color" codeModel={<ColorButtonGroupCode />}>
                <ColorButtonGroup />
              </ChildCard>
            </Grid>
          </Grid>
        </ParentCard>
      </Grid>
    </Grid>
  </PageContainer>)
);
export default ExButton;
