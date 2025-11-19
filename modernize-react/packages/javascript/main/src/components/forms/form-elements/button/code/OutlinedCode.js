import CodeDialog from '../../../../shared/CodeDialog';
import React from 'react';
const OutlinedCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { Button, Stack } from '@mui/material';

<Stack spacing={1} direction={{ xs: 'column', sm: 'row' }} justifyContent="center">
    <Button variant="outlined" color="primary">
      Primary
    </Button>
    <Button variant="outlined" color="secondary">
      Secondary
    </Button>
    <Button variant="outlined" color="error">
      Error
    </Button>
    <Button variant="outlined" color="warning">
      Warning
    </Button>
    <Button variant="outlined" color="success">
      Success
    </Button>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default OutlinedCode;
