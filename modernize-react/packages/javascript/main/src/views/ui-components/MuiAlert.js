import React from 'react';
import { IconX } from '@tabler/icons';
import { Grid } from '@mui/material';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import Collapse from '@mui/material/Collapse';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';

import Breadcrumb from '../../layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from '../../components/container/PageContainer';
import ParentCard from '../../components/shared/ParentCard';
import ChildCard from '../../components/shared/ChildCard';

import FilledCode from '../../components/material-ui/alert/code/FilledCode';
import OutlinedCode from '../../components/material-ui/alert/code/OutlinedCode';
import DescriptionCode from '../../components/material-ui/alert/code/DescriptionCode';
import ActionCode from '../../components/material-ui/alert/code/ActionCode';
import TransitionCode from '../../components/material-ui/alert/code/TransitionCode';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Alert',
  },
];

const ExAlert = () => {
  const [open, setOpen] = React.useState(true);

  return (
    <PageContainer title="Alert" description="this is Alert page">
      {/* breadcrumb */}
      <Breadcrumb title="Alert" items={BCrumb} />
      {/* end breadcrumb */}
      {/* ------------------------- row 1 ------------------------- */}

      <ParentCard title="Alert">
        <Grid container spacing={3}>
          {/* --------------------------------------------------------------------------------- */}
          {/* Basic Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid size={12} display="flex" alignItems="stretch">
            <ChildCard title="Basic">
              <Stack spacing={1}>
                <Alert severity="error" icon={false}>
                  This is an error alert — check it out!
                </Alert>
                <Alert severity="warning" icon={false}>
                  This is a warning alert — check it out!
                </Alert>
                <Alert severity="info" icon={false}>
                  This is an info alert — check it out!
                </Alert>
                <Alert severity="success" icon={false}>
                  This is a success alert — check it out!
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Filled Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid size={12} display="flex" alignItems="stretch">
            <ChildCard title="Filled" codeModel={<FilledCode />}>
              <Stack spacing={1}>
                <Alert variant="filled" onClose={() => { }} severity="error">
                  This is an error alert — check it out!
                </Alert>
                <Alert variant="filled" onClose={() => { }} severity="warning">
                  This is a warning alert — check it out!
                </Alert>
                <Alert variant="filled" onClose={() => { }} severity="info">
                  This is an info alert — check it out!
                </Alert>
                <Alert variant="filled" onClose={() => { }} severity="success">
                  This is a success alert — check it out!
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Outlined Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid size={12} display="flex" alignItems="stretch">
            <ChildCard title="Outlined" codeModel={<OutlinedCode />}>
              <Stack spacing={1}>
                <Alert variant="outlined" onClose={() => { }} severity="error">
                  This is an error alert — check it out!
                </Alert>
                <Alert variant="outlined" onClose={() => { }} severity="warning">
                  This is a warning alert — check it out!
                </Alert>
                <Alert variant="outlined" onClose={() => { }} severity="info">
                  This is an info alert — check it out!
                </Alert>
                <Alert variant="outlined" onClose={() => { }} severity="success">
                  This is a success alert — check it out!
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Description Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid size={12} display="flex" alignItems="stretch">
            <ChildCard title="Description" codeModel={<DescriptionCode />}>
              <Stack spacing={1}>
                <Alert severity="error">
                  <AlertTitle>Error</AlertTitle>
                  This is an error alert — <strong>check it out!</strong>
                </Alert>
                <Alert severity="warning">
                  <AlertTitle>Warning</AlertTitle>
                  This is a warning alert — <strong>check it out!</strong>
                </Alert>
                <Alert severity="info">
                  <AlertTitle>Info</AlertTitle>
                  This is an info alert — <strong>check it out!</strong>
                </Alert>
                <Alert severity="success">
                  <AlertTitle>Success</AlertTitle>
                  This is a success alert — <strong>check it out!</strong>
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Action Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid size={12} display="flex" alignItems="stretch">
            <ChildCard title="Action" codeModel={<ActionCode />}>
              <Stack spacing={1}>
                <Alert variant="filled" severity="warning" onClose={() => { }}>
                  This is a success alert — check it out!
                </Alert>
                <Alert
                  variant="filled"
                  severity="info"
                  action={
                    <Button color="inherit" size="small">
                      UNDO
                    </Button>
                  }
                >
                  This is a success alert — check it out!
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Transition Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid size={12} display="flex" alignItems="stretch">
            <ChildCard title="Transition" codeModel={<TransitionCode />}>
              <Stack spacing={1}>
                <Collapse in={open}>
                  <Alert
                    variant="filled"
                    severity="info"
                    sx={{ mb: 1 }}
                    action={
                      <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => {
                          setOpen(false);
                        }}
                      >
                        <IconX width={20} />
                      </IconButton>
                    }
                  >
                    Close me!
                  </Alert>
                </Collapse>
              </Stack>
              <Button
                disabled={open}
                variant="contained"
                onClick={() => {
                  setOpen(true);
                }}
              >
                Re-open
              </Button>
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>
  );
};

export default ExAlert;
