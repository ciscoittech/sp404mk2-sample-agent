// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Box, Button, ButtonGroup } from '@mui/material';
import { IconFolder, IconActivity, IconTag } from '@tabler/icons-react';

const EmailActions = () => {
  return (
    <Box sx={{ p: 2 }}>
      <ButtonGroup size="small" aria-label="small button group" fullWidth>
        {/* ------------------------------------------- */}
        {/* Action buttons */}
        {/* ------------------------------------------- */}
        <Button key="one">
          <IconActivity width="17" />
        </Button>
        <Button key="two">
          <IconFolder width="17" />
        </Button>
        <Button key="three">
          <IconTag width="17" />
        </Button>
      </ButtonGroup>
    </Box>
  );
};

export default EmailActions;
