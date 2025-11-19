import CodeDialog from '../../../shared/CodeDialog';

const ActionCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import {
  Stack,
  Button,
  Alert,
} from "@mui/material";

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
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default ActionCode;
