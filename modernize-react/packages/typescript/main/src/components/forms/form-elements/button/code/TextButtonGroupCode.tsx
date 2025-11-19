import CodeDialog from 'src/components/shared/CodeDialog';
const TextButtonGroupCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Button, ButtonGroup, Stack } from '@mui/material';

<Stack spacing={1} direction="column" justifyContent="center">
    <ButtonGroup variant="text" aria-label="text button group">
      <Button>One</Button>
      <Button>Two</Button>
      <Button>Three</Button>
    </ButtonGroup>
    <ButtonGroup color="secondary" variant="text" aria-label="text button group">
      <Button>One</Button>
      <Button>Two</Button>
      <Button>Three</Button>
    </ButtonGroup>
    <ButtonGroup color="error" variant="text" aria-label="text button group">
      <Button>One</Button>
      <Button>Two</Button>
      <Button>Three</Button>
    </ButtonGroup>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default TextButtonGroupCode;
