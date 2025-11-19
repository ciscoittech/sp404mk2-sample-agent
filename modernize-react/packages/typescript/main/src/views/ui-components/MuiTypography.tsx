// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Typography, Grid } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';

// CodeModels
import Heading1Code from 'src/components/material-ui/typography/code/Heading1Code';
import Heading2Code from 'src/components/material-ui/typography/code/Heading2Code';
import Heading3Code from 'src/components/material-ui/typography/code/Heading3Code';
import Heading4Code from 'src/components/material-ui/typography/code/Heading4Code';
import Heading5Code from 'src/components/material-ui/typography/code/Heading5Code';
import Heading6Code from 'src/components/material-ui/typography/code/Heading6Code';
import Subtitle1Code from 'src/components/material-ui/typography/code/Subtitle1Code';
import Subtitle2Code from 'src/components/material-ui/typography/code/Subtitle2Code';
import TextPrimaryCode from 'src/components/material-ui/typography/code/TextPrimaryCode';
import TextSecondaryCode from 'src/components/material-ui/typography/code/TextSecondaryCode';
import TextInfoCode from 'src/components/material-ui/typography/code/TextInfoCode';
import TextWarningCode from 'src/components/material-ui/typography/code/TextWarningCode';
import TextErrorCode from 'src/components/material-ui/typography/code/TextErrorCode';
import TextSuccessCode from 'src/components/material-ui/typography/code/TextSuccessCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Typography',
  },
];

const CustomTypography = () => {
  return (
    (<PageContainer title="Typography" description="this is Typography page">
      {/* breadcrumb */}
      <Breadcrumb title="Typography" items={BCrumb} />
      {/* end breadcrumb */}
      <Grid container spacing={3}>
        <Grid
          size={{
            sm: 12
          }}>
          <ParentCard title="Default Text">
            <Grid container spacing={3}>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Heading " codeModel={<Heading1Code />}>
                  <Typography variant="h1">h1. Heading</Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 30 | line-height: 45 | font weight: 500
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Heading " codeModel={<Heading2Code />}>
                  <Typography variant="h2">h2. Heading</Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 24 | line-height: 36 | font weight: 500
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Heading " codeModel={<Heading3Code />}>
                  <Typography variant="h3">h3. Heading</Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 21 | line-height: 31.5 | font weight: 500
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Heading " codeModel={<Heading4Code />}>
                  <Typography variant="h4">h4. Heading</Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 18 | line-height: 27 | font weight: 500
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Heading" codeModel={<Heading5Code />}>
                  <Typography variant="h5">h5. Heading</Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 16 | line-height: 24 | font weight: 500
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Heading " codeModel={<Heading6Code />}>
                  <Typography variant="h6">h6. Heading</Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 14 | line-height: 21 | font weight: 500
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Subtitle" codeModel={<Subtitle1Code />}>
                  <Typography variant="subtitle1">
                    subtitle1. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis
                    tenetur
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 16 | line-height: 28 | font weight: 400
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Subtitle" codeModel={<Subtitle2Code />}>
                  <Typography variant="subtitle2">
                    subtitle2. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis
                    tenetur
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 14 | line-height: 21 | font weight: 400
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard>
                  <Typography variant="body1">
                    body1. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 16 | line-height: 24 | font weight: 400
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard>
                  <Typography variant="body2">
                    body2. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 14 | line-height: 20 | font weight: 400
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard>
                  <Typography variant="caption">
                    caption. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis
                    tenetur
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 12 | line-height: 19 | font weight: 400
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard>
                  <Typography variant="overline">
                    overline. Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis
                    tenetur
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    font size: 12 | line-height: 31 | font weight: 400
                  </Typography>
                </ChildCard>
              </Grid>
            </Grid>

          </ParentCard>
        </Grid>
        <Grid
          size={{
            sm: 12
          }}>
          <ParentCard title="Default Text">
            <Grid container spacing={3}>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard>
                  <Typography variant="h5" color="textprimary">
                    Text Primary
                  </Typography>

                  <Typography variant="body1" color="textprimary">
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Text Secondary" codeModel={<TextSecondaryCode />}>
                  <Typography variant="h5" color="textSecondary">
                    Text Secondary
                  </Typography>

                  <Typography variant="body1" color="textSecondary">
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Text Info" codeModel={<TextInfoCode />}>
                  <Typography variant="h5" sx={{ color: (theme) => theme.palette.info.main }}>
                    Text Info
                  </Typography>

                  <Typography variant="body1" sx={{ color: (theme) => theme.palette.info.main }}>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Text Primary" codeModel={<TextPrimaryCode />}>
                  <Typography variant="h5" sx={{ color: (theme) => theme.palette.primary.main }}>
                    Text Primary
                  </Typography>

                  <Typography variant="body1" sx={{ color: (theme) => theme.palette.primary.main }}>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Text Warning" codeModel={<TextWarningCode />}>
                  <Typography variant="h5" sx={{ color: (theme) => theme.palette.warning.main }}>
                    Text Warning
                  </Typography>

                  <Typography variant="body1" sx={{ color: (theme) => theme.palette.warning.main }}>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Text Error" codeModel={<TextErrorCode />}>
                  <Typography variant="h5" sx={{ color: (theme) => theme.palette.error.main }}>
                    Text Error
                  </Typography>

                  <Typography variant="body1" sx={{ color: (theme) => theme.palette.error.main }}>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
              <Grid
                size={{
                  sm: 12
                }}>
                <ChildCard title="Text Success" codeModel={<TextSuccessCode />}>
                  <Typography variant="h5" sx={{ color: (theme) => theme.palette.success.main }}>
                    Text Success
                  </Typography>

                  <Typography variant="body1" sx={{ color: (theme) => theme.palette.success.main }}>
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
                  </Typography>
                </ChildCard>
              </Grid>
            </Grid>
          </ParentCard>
        </Grid>
      </Grid >
    </PageContainer >)
  );
};

export default CustomTypography;
