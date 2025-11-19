import CodeDialog from 'src/components/shared/CodeDialog';

const SizesSwitchCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Box, Switch } from '@mui/material';

<Box textAlign="center">
    <Switch defaultChecked size="small" />
    <Switch defaultChecked />
</Box>
`}
      </CodeDialog>
    </>
  );
};

export default SizesSwitchCode;
