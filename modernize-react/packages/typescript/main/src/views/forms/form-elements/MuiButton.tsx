// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';

import DefaultButtons from 'src/components/forms/form-elements/button/DefaultButtons';
import ColorButtons from 'src/components/forms/form-elements/button/ColorButtons';
import IconLoadingButtons from 'src/components/forms/form-elements/button/IconLoadingButtons';
import SizeButton from 'src/components/forms/form-elements/button/SizeButton';

import OutlinedIconButtons from 'src/components/forms/form-elements/button/OutlinedIconButtons';
import OutlinedSizeButton from 'src/components/forms/form-elements/button/OutlinedSizeButton';

import TextDefaultButtons from 'src/components/forms/form-elements/button/TextDefaultButtons';
import TextColorButtons from 'src/components/forms/form-elements/button/TextColorButtons';
import TextIconButtons from 'src/components/forms/form-elements/button/TextIconButtons';
import TextSizeButton from 'src/components/forms/form-elements/button/TextSizeButton';

import IconColorButtons from 'src/components/forms/form-elements/button/IconColorButtons';
import IconSizeButtons from 'src/components/forms/form-elements/button/IconSizeButtons';

import FabDefaultButton from 'src/components/forms/form-elements/button/FabDefaultButton';
import FabColorButtons from 'src/components/forms/form-elements/button/FabColorButtons';
import FabSizeButtons from 'src/components/forms/form-elements/button/FabSizeButtons';

import DefaultButtonGroup from 'src/components/forms/form-elements/button/DefaultButtonGroup';
import SizeButtonGroup from 'src/components/forms/form-elements/button/SizeButtonGroup';
import VerticalButtonGroup from 'src/components/forms/form-elements/button/VerticalButtonGroup';
import ColorButtonGroup from 'src/components/forms/form-elements/button/ColorButtonGroup';
import TextButtonGroup from 'src/components/forms/form-elements/button/TextButtonGroup';
import OutlinedColorButtons from '../../../components/forms/form-elements/button/OutlinedColorButtons';

// codeModel
import DefaultCode from 'src/components/forms/form-elements/button/code/DefaultCode';
import ColorsCode from 'src/components/forms/form-elements/button/code/ColorsCode';
import LoadingButtonsCode from 'src/components/forms/form-elements/button/code/LoadingButtonsCode';
import SizesCode from 'src/components/forms/form-elements/button/code/SizesCode';
import OutlinedCode from 'src/components/forms/form-elements/button/code/OutlinedCode';
import OutlinedIconCode from 'src/components/forms/form-elements/button/code/OutlinedIconCode';
import OutlineSizeCode from 'src/components/forms/form-elements/button/code/OutlineSizeCode';
import TextCode from 'src/components/forms/form-elements/button/code/TextCode';
import TextColorCode from 'src/components/forms/form-elements/button/code/TextColorCode';
import TextIconColor from 'src/components/forms/form-elements/button/code/TextIconColor';
import TextSizesCode from 'src/components/forms/form-elements/button/code/TextSizesCode';
import IconColorCode from 'src/components/forms/form-elements/button/code/IconColorCode';
import IconSizesCode from 'src/components/forms/form-elements/button/code/IconSizesCode';
import FABCode from 'src/components/forms/form-elements/button/code/FABCode';
import FABColorCode from 'src/components/forms/form-elements/button/code/FABColorCode';
import FABSizeCode from 'src/components/forms/form-elements/button/code/FABSizeCode';
import DefaultButtonGroupCode from 'src/components/forms/form-elements/button/code/DefaultButtonGroupCode';
import SizeButtonGroupCode from 'src/components/forms/form-elements/button/code/SizeButtonGroupCode';
import VerticalButtonGroupCode from 'src/components/forms/form-elements/button/code/VerticalButtonGroupCode';
import TextButtonGroupCode from 'src/components/forms/form-elements/button/code/TextButtonGroupCode';
import ColorButtonGroupCode from 'src/components/forms/form-elements/button/code/ColorButtonGroupCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Button',
  },
];

const MuiButton = () => (
  <PageContainer title="Buttons" description="this is Buttons page">
    {/* breadcrumb */}
    <Breadcrumb title="Button" items={BCrumb} />
    {/* end breadcrumb */}
    <Grid container spacing={3}>
      <Grid size={12}>
        <ParentCard title='Buttons'>
          <Grid container spacing={3}>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Default" codeModel={<DefaultCode />}>
                <DefaultButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Colors" codeModel={<ColorsCode />}>
                <ColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Loading Buttons" codeModel={<LoadingButtonsCode />}>
                <IconLoadingButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Sizes" codeModel={<SizesCode />}>
                <SizeButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Outlined" codeModel={<OutlinedCode />}>
                <OutlinedColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Outlined Icon" codeModel={<OutlinedIconCode />}>
                <OutlinedIconButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Outline Size" codeModel={<OutlineSizeCode />}>
                <OutlinedSizeButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Text" codeModel={<TextCode />}>
                <TextDefaultButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Text Color" codeModel={<TextColorCode />}>
                <TextColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Text Icon" codeModel={<TextIconColor />}>
                <TextIconButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Text Sizes" codeModel={<TextSizesCode />}>
                <TextSizeButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Icon Color" codeModel={<IconColorCode />}>
                <IconColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Icon Sizes" codeModel={<IconSizesCode />}>
                <IconSizeButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="FAB" codeModel={<FABCode />}>
                <FabDefaultButton />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="FAB Color" codeModel={<FABColorCode />}>
                <FabColorButtons />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="FAB Size" codeModel={<FABSizeCode />}>
                <FabSizeButtons />
              </ChildCard>
            </Grid>
          </Grid>
        </ParentCard>
      </Grid>
      <Grid size={12}>
        <ParentCard title='Button Group'>
          <Grid container spacing={3}>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Default" codeModel={<DefaultButtonGroupCode />}>
                <DefaultButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Sizes" codeModel={<SizeButtonGroupCode />}>
                <SizeButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Verical" codeModel={<VerticalButtonGroupCode />}>
                <VerticalButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid
              display="flex"
              alignItems="stretch"
              size={{
                xs: 12,
                lg: 6
              }}>
              <ChildCard title="Text" codeModel={<TextButtonGroupCode />}>
                <TextButtonGroup />
              </ChildCard>
            </Grid>
            {/* ------------------------- row 1 ------------------------- */}
            <Grid display="flex" alignItems="stretch" size={12}>
              <ChildCard title="Color" codeModel={<ColorButtonGroupCode />}>
                <ColorButtonGroup />
              </ChildCard>
            </Grid>
          </Grid>
        </ParentCard>
      </Grid>
    </Grid>
  </PageContainer >
);
export default MuiButton;
