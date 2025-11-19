import CodeDialog from 'src/components/shared/CodeDialog';
const OutlinedIconCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Button, Stack } from '@mui/material';
import { IconTrash, IconSend } from '@tabler/icons-react';

<Stack spacing={1} direction={{ xs: 'column', sm: 'row' }} justifyContent="center">
    <Button
        variant="outlined"
        color="error"
        startIcon={<IconTrash width={18} />}
    >
        Left Icon
    </Button>
    <Button
        variant="outlined"
        color="secondary"
        endIcon={<IconSend width={18} />}
    >
        Right Icon
    </Button>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default OutlinedIconCode;
