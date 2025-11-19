import CodeDialog from 'src/components/shared/CodeDialog';
const VerticalButtonGroupCode = () => {
  return (
    <>
      <CodeDialog>
        {`
  "use client";
  
  import { Button, ButtonGroup, Stack } from '@mui/material';

  <Stack spacing={1} direction="row">
      <ButtonGroup
        orientation="vertical"
        variant="contained"
        aria-label="outlined primary button group"
      >
        <Button>One</Button>
        <Button>Two</Button>
        <Button>Three</Button>
      </ButtonGroup>

      <ButtonGroup orientation="vertical" variant="outlined" aria-label="outlined button group">
        <Button>One</Button>
        <Button>Two</Button>
        <Button>Three</Button>
      </ButtonGroup>

      <ButtonGroup orientation="vertical" variant="text" aria-label="text button group">
        <Button>One</Button>
        <Button>Two</Button>
        <Button>Three</Button>
      </ButtonGroup>
  </Stack>`}
      </CodeDialog>
    </>
  );
};

export default VerticalButtonGroupCode;
