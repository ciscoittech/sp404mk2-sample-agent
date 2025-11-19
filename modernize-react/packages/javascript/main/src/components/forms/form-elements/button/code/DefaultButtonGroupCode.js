import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const DefaultButtonGroupCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import {  Button, ButtonGroup, Stack } from '@mui/material';

<Stack spacing={1} >
    <ButtonGroup variant="outlined" aria-label="outlined button group">
        <Button>One</Button>
        <Button>Two</Button>
        <Button>Three</Button>
    </ButtonGroup>
    <ButtonGroup variant="contained" aria-label="outlined primary button group">
        <Button>One</Button>
        <Button>Two</Button>
        <Button>Three</Button>
    </ButtonGroup>
    <ButtonGroup variant="text" aria-label="text button group">
        <Button>One</Button>
        <Button>Two</Button>
        <Button>Three</Button>
    </ButtonGroup>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default DefaultButtonGroupCode;
