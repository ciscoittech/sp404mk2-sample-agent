// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { styled } from '@mui/material/styles';
import { Grid, IconButton, Button, Stack, Fab, Box } from '@mui/material';
import Tooltip, { TooltipProps, tooltipClasses } from '@mui/material/Tooltip';
import Fade from '@mui/material/Fade';
import Zoom from '@mui/material/Zoom';
import InlineItemCard from "src/components/shared/InlineItemCard";

// common component
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';

// CodeModels
import SimpleTooltipCode from 'src/components/material-ui/tooltip/code/SimpleTooltipCode';
import ArrowTooltipCode from 'src/components/material-ui/tooltip/code/ArrowTooltipCode';
import VariableWidthCode from 'src/components/material-ui/tooltip/code/VariableWidthCode';
import TransitionsCode from 'src/components/material-ui/tooltip/code/TransitionsCode';
import PositionsTooltipCode from 'src/components/material-ui/tooltip/code/PositionsTooltipCode';

import { IconPlus, IconTrash } from '@tabler/icons-react';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Tooltip',
  },
];

// variable width
const CustomWidthTooltip = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))({
  [`& .${tooltipClasses.tooltip}`]: {
    maxWidth: 500,
  },
});

const NoMaxWidthTooltip = styled(({ className, ...props }: TooltipProps) => (
  <Tooltip {...props} classes={{ popper: className }} />
))({
  [`& .${tooltipClasses.tooltip}`]: {
    maxWidth: 'none',
  },
});

const longText = `
Aliquam eget finibus ante, non facilisis lectus. Sed vitae dignissim est, vel aliquam tellus.
Praesent non nunc mollis, fermentum neque at, semper arcu.
Nullam eget est sed sem iaculis gravida eget vitae justo.
`;

const MuiTooltip = () => (
  <PageContainer title="Tooltip" description="this is Tooltip page">
    {/* breadcrumb */}
    <Breadcrumb title="Tooltip" items={BCrumb} />
    {/* end breadcrumb */}

    <ParentCard title="Tooltip">
      <Grid container spacing={3}>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Simple" codeModel={<SimpleTooltipCode />}>
            <Stack direction="row" spacing={2} alignItems="center">
              <Tooltip title="Delete">
                <IconButton>
                  <IconTrash width={20} height={20} />
                </IconButton>
              </Tooltip>
              <Tooltip title="Add">
                <Button variant="outlined" color="primary">
                  Button
                </Button>
              </Tooltip>
              <Tooltip title="Delete">
                <IconButton color="error">
                  <IconTrash width={20} height={20} />
                </IconButton>
              </Tooltip>
              <Tooltip title="Add">
                <Fab color="secondary">
                  <IconPlus width={20} height={20} />
                </Fab>
              </Tooltip>
            </Stack>
          </ChildCard>
        </Grid>
        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Arrow" codeModel={<ArrowTooltipCode />}>
            <Box textAlign="center">
              <Tooltip title="Delete" arrow>
                <Fab color="secondary">
                  <IconPlus width={20} height={20} />
                </Fab>
              </Tooltip>
            </Box>

          </ChildCard>
        </Grid>

        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Variable Width" codeModel={<VariableWidthCode />}>
            <Stack spacing={1} direction="row">
              <Tooltip title={longText}>
                <Button variant="outlined">Default Width [300px]</Button>
              </Tooltip>
              <CustomWidthTooltip title={longText}>
                <Button color="secondary" variant="outlined">Custom Width [500px]</Button>
              </CustomWidthTooltip>
              <NoMaxWidthTooltip title={longText}>
                <Button color="warning" variant="outlined">No wrapping</Button>
              </NoMaxWidthTooltip>
            </Stack>

          </ChildCard>
        </Grid>

        <Grid
          display="flex"
          alignItems="stretch"
          size={{
            xs: 12,
            sm: 6
          }}>
          <ChildCard title="Transitions" codeModel={<TransitionsCode />}>
            <Stack spacing={1} direction="row">
              <Tooltip title="Add">
                <Button variant="outlined" color="primary">Grow</Button>
              </Tooltip>
              <Tooltip
                title="Add"
                slots={{
                  transition: Fade
                }}
                slotProps={{
                  transition: { timeout: 600 }
                }}
              >
                <Button variant="outlined" color="secondary">Fade</Button>
              </Tooltip>
              <Tooltip title="Add" slots={{
                transition: Zoom
              }}>
                <Button variant="outlined" color="warning">Zoom</Button>
              </Tooltip>
            </Stack>

          </ChildCard>
        </Grid>
        <Grid display="flex" alignItems="stretch" size={12}>
          <ChildCard title="Positions" codeModel={<PositionsTooltipCode />}>
            <InlineItemCard>
              <Tooltip title="Top Start" placement="top-start">
                <Button variant="outlined" color="primary">Top Start</Button>
              </Tooltip>
              <Tooltip title="Top" placement="top">
                <Button variant="outlined" color="secondary">Top</Button>
              </Tooltip>
              <Tooltip title="Top End" placement="top-end">
                <Button variant="outlined" color="warning">Top End</Button>
              </Tooltip>
              <Tooltip title="Left Start" placement="left-start">
                <Button variant="outlined" color="success">Left Start</Button>
              </Tooltip>
              <Tooltip title="Left" placement="left">
                <Button variant="outlined" color="error">Left</Button>
              </Tooltip>
              <Tooltip title="Left End" placement="left-end">
                <Button variant="outlined" color="primary">Left End</Button>
              </Tooltip>
              <Tooltip title="Right Start" placement="right-start">
                <Button variant="outlined" color="secondary">Right Start</Button>
              </Tooltip>
              <Tooltip title="Right" placement="right">
                <Button variant="outlined" color="warning">Right</Button>
              </Tooltip>
              <Tooltip title="Right End" placement="right-end">
                <Button variant="outlined" color="success">Right End</Button>
              </Tooltip>
              <Tooltip title="Bottom Start" placement="bottom-start">
                <Button variant="outlined" color="error">Bottom Start</Button>
              </Tooltip>
              <Tooltip title="Bottom" placement="bottom">
                <Button variant="outlined" color="primary">Bottom</Button>
              </Tooltip>
              <Tooltip title="Bottom End" placement="bottom-end">
                <Button variant="outlined" color="secondary">Bottom End</Button>
              </Tooltip>
            </InlineItemCard>
          </ChildCard>
        </Grid>
      </Grid>
    </ParentCard>
  </PageContainer>
);
export default MuiTooltip;
