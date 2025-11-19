import CodeDialog from '../../../shared/CodeDialog';

const VariantCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Avatar, Stack } from '@mui/material';
import { IconMoodSmile } from '@tabler/icons';

<Stack direction="row" spacing={1} justifyContent="center">
    <Avatar sx={{ bgcolor: 'primary.main' }}>
        <IconMoodSmile width={24} />
    </Avatar>
    <Avatar sx={{ bgcolor: 'primary.main' }} variant="square">
        <IconMoodSmile width={24} />
    </Avatar>
    <Avatar sx={{ bgcolor: 'primary.main' }} variant="rounded">
        <IconMoodSmile width={24} />
    </Avatar>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default VariantCode;
