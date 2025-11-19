import CodeDialog from '../../../shared/CodeDialog';

const ImageAvatarsCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Avatar, Stack } from '@mui/material';

<Stack direction="row" spacing={1} justifyContent="center">
    <Avatar alt="Remy Sharp" src={User1} />
    <Avatar alt="Travis Howard" src={User2} />
    <Avatar alt="Cindy Baker" src={User3} />
</Stack>
`}
      </CodeDialog>
    </>
  );
};

export default ImageAvatarsCode;
