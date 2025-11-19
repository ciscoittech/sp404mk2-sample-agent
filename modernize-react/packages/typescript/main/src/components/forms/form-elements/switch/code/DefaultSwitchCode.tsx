import CodeDialog from 'src/components/shared/CodeDialog';

const DefaultSwitchCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Box, Switch } from '@mui/material';

<Box textAlign="center">
    <Switch defaultChecked />
    <Switch />
    <Switch disabled defaultChecked />
    <Switch disabled />
</Box>
`}
      </CodeDialog>
    </>
  );
};

export default DefaultSwitchCode;
