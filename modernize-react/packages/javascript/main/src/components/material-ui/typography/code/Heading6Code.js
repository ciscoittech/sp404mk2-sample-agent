import CodeDialog from '../../../shared/CodeDialog';

const Heading6Code = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Typography } from '@mui/material';

<Typography variant="h6">h6. Heading</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Heading6Code;
