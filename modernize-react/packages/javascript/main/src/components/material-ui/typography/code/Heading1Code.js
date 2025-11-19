import CodeDialog from '../../../shared/CodeDialog';

const Heading1Code = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Typography } from '@mui/material';

<Typography variant="h1">h1. Heading</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Heading1Code;
