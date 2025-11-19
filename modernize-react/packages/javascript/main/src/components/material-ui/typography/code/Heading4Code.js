import CodeDialog from '../../../shared/CodeDialog';

const Heading4Code = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Typography } from '@mui/material';

<Typography variant="h4">h4. Heading</Typography>`}
      </CodeDialog>
    </>
  );
};

export default Heading4Code;
