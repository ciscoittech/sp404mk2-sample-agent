import CodeDialog from "src/components/shared/CodeDialog";
const TextCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Button, Stack } from '@mui/material';

<Stack spacing={1} direction={{ xs: 'column', sm: 'row' }} justifyContent="center">
    <Button color="primary">Primary</Button>
    <Button color="secondary">Secondary</Button>
    <Button disabled>Disabled</Button>
    <Button href="#text-buttons" color="primary">
      Link
    </Button>
</Stack>`}
      </CodeDialog>
    </>
  )
}

export default TextCode
