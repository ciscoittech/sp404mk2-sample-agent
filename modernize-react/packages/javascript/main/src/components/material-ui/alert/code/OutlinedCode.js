import CodeDialog from '../../../shared/CodeDialog';

const OutlinedCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import {
  Stack,
  Alert,
} from "@mui/material";

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
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default OutlinedCode;
