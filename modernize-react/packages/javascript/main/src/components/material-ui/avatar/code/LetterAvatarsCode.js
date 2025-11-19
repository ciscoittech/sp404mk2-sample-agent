import CodeDialog from '../../../shared/CodeDialog';

const LetterAvatarsCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Avatar, Stack } from '@mui/material';


<Stack direction="row" spacing={1} justifyContent="center">
    <Avatar sx={{ bgcolor: 'primary.main' }}>A</Avatar>
    <Avatar sx={{ bgcolor: 'secondary.main' }}>B</Avatar>
    <Avatar sx={{ bgcolor: 'error.main' }}>C</Avatar>
    <Avatar sx={{ bgcolor: 'warning.main' }}>D</Avatar>
    <Avatar sx={{ bgcolor: 'success.main' }}>E</Avatar>
</Stack>
`}
      </CodeDialog>
    </>
  );
};

export default LetterAvatarsCode;
