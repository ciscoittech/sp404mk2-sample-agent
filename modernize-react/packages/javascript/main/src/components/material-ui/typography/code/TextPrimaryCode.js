import CodeDialog from '../../../shared/CodeDialog';

const TextPrimaryCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Typography } from '@mui/material';

<Typography variant="body1" sx={{ color: (theme) => theme.palette.primary.main }}>
    Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quos blanditiis tenetur
</Typography>`}
      </CodeDialog>
    </>
  );
};

export default TextPrimaryCode;
