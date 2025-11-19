import CodeDialog from '../../../shared/CodeDialog';

const Heading2Code = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Typography } from '@mui/material';

<Typography variant="h2">h2. Heading</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Heading2Code;
