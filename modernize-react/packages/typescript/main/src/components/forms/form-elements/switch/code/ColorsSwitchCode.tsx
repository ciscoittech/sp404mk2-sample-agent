import CodeDialog from 'src/components/shared/CodeDialog';

const ColorsSwitchCode = () => {
  return (
    <>
      <CodeDialog>
        {`
"use client";

import { Box, Switch } from '@mui/material';

<Box textAlign="center">
    <Switch defaultChecked />
    <Switch defaultChecked color="secondary" />
    <Switch defaultChecked color="error" />
    <Switch defaultChecked color="warning" />
    <Switch defaultChecked color="success" />
    <Switch defaultChecked color="default" />
</Box>
`}
      </CodeDialog>
    </>
  );
};

export default ColorsSwitchCode;
