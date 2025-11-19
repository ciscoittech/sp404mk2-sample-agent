import CodeDialog from 'src/components/shared/CodeDialog';
const TextSizesCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Button, Stack } from '@mui/material';

<Stack spacing={1} direction="row" alignItems="center" justifyContent="center">
    <Button size="small">Small</Button>
    <Button size="medium">Medium</Button>
    <Button size="large">Large</Button>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default TextSizesCode;
