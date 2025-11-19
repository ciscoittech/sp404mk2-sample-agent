import CodeDialog from '../../../shared/CodeDialog';

const ArrowTooltipCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { styled } from '@mui/material/styles';
import { IconButton, Button, Stack, Fab, Box } from '@mui/material';
import Tooltip, { TooltipProps, tooltipClasses } from '@mui/material/Tooltip';

import { IconPlus } from '@tabler/icons';

<Box textAlign="center">
    <Tooltip title="Delete" arrow>
        <Fab color="secondary">
            <IconPlus width={20} height={20} />
        </Fab>
    </Tooltip>
</Box>
`}
      </CodeDialog>
    </>
  );
};

export default ArrowTooltipCode;
