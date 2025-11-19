import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const ColorsCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import {  Button, Stack } from '@mui/material';

<Stack gap={1} direction={{ xs: 'column', sm: 'row' }} justifyContent="center">
    <Button variant="contained" color="primary">
        Primary
    </Button>
    <Button variant="contained" color="secondary">
        Secondary
    </Button>
    <Button variant="contained" color="error">
        Error
    </Button>
    <Button variant="contained" color="warning">
        Warning
    </Button>
    <Button variant="contained" color="success">
        Success
    </Button>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default ColorsCode;
