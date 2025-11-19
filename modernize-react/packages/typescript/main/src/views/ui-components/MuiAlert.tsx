// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { IconX } from "@tabler/icons-react";
import { Grid, Stack, Button, IconButton, Collapse, Alert, AlertTitle } from '@mui/material';

import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';

import FilledCode from "src/components/material-ui/alert/code/FilledCode";
import OutlinedCode from "src/components/material-ui/alert/code/OutlinedCode";
import DescriptionCode from "src/components/material-ui/alert/code/DescriptionCode";
import ActionCode from "src/components/material-ui/alert/code/ActionCode";
import TransitionCode from "src/components/material-ui/alert/code/TransitionCode";

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
    (<PageContainer title="Alert" description="this is Alert page">
      {/* breadcrumb */}
      <Breadcrumb title="Alert" items={BCrumb} />
      {/* end breadcrumb */}
      {/* ------------------------- row 1 ------------------------- */}
      <ParentCard title="Alert">
        <Grid container spacing={3}>
          {/* --------------------------------------------------------------------------------- */}
          {/* Filled Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid display="flex" alignItems="stretch" size={12}>
            <ChildCard title="Filled" codeModel={<FilledCode />}>
              <Stack spacing={1}>
                <Alert variant="filled" severity="error">
                  This is an error alert — check it out!
                </Alert>
                <Alert variant="filled" severity="warning">
                  This is a warning alert — check it out!
                </Alert>
                <Alert variant="filled" severity="info">
                  This is an info alert — check it out!
                </Alert>
                <Alert variant="filled" severity="success">
                  This is a success alert — check it out!
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Outlined Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid display="flex" alignItems="stretch" size={12}>
            <ChildCard title="Outlined" codeModel={<OutlinedCode />}>
              <Stack spacing={1}>
                <Alert variant="outlined" severity="error">
                  This is an error alert — check it out!
                </Alert>
                <Alert variant="outlined" severity="warning">
                  This is a warning alert — check it out!
                </Alert>
                <Alert variant="outlined" severity="info">
                  This is an info alert — check it out!
                </Alert>
                <Alert variant="outlined" severity="success">
                  This is a success alert — check it out!
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Description Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid display="flex" alignItems="stretch" size={12}>
            <ChildCard title="Description" codeModel={<DescriptionCode />}>
              <Stack spacing={1}>
                <Alert variant="filled" severity="error">
                  <AlertTitle>Error</AlertTitle>
                  This is an error alert — <strong>check it out!</strong>
                </Alert>
                <Alert variant="filled" severity="warning">
                  <AlertTitle>Warning</AlertTitle>
                  This is a warning alert — <strong>check it out!</strong>
                </Alert>
                <Alert variant="filled" severity="info">
                  <AlertTitle>Info</AlertTitle>
                  This is an info alert — <strong>check it out!</strong>
                </Alert>
                <Alert variant="filled" severity="success">
                  <AlertTitle>Success</AlertTitle>
                  This is a success alert — <strong>check it out!</strong>
                </Alert>
              </Stack>
            </ChildCard>
          </Grid>
          {/* --------------------------------------------------------------------------------- */}
          {/* Action Alert */}
          {/* --------------------------------------------------------------------------------- */}
          <Grid display="flex" alignItems="stretch" size={12}>
            <ChildCard title="Action" codeModel={<ActionCode />}>
              <Stack spacing={1}>
                <Alert variant="filled" severity="warning">
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
          <Grid display="flex" alignItems="stretch" size={12}>
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
    </PageContainer>)
  );
};

export default ExAlert;
