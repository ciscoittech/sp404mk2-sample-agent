import CodeDialog from 'src/components/shared/CodeDialog';
const SizesCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Button, Stack } from '@mui/material';

<Stack spacing={1} direction={{ xs: 'column', sm: 'row' }} alignItems="center" justifyContent="center">
    <Button variant="contained" size="small">
      Small
    </Button>
    <Button variant="contained" size="medium">
      Medium
    </Button>
    <Button variant="contained" size="large">
      Large
    </Button>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default SizesCode;
