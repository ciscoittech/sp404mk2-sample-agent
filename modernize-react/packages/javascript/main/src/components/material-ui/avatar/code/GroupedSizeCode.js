import CodeDialog from '../../../shared/CodeDialog';

const GroupedSizeCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Avatar, AvatarGroup, Stack } from '@mui/material';


<Stack direction="row" spacing={1} justifyContent="center">
    <AvatarGroup max={4}>
        <Avatar alt="Remy Sharp" sx={{ width: 56, height: 56 }} src={User1} />
        <Avatar alt="Travis Howard" sx={{ width: 56, height: 56 }} src={User2} />
        <Avatar alt="Cindy Baker" sx={{ width: 56, height: 56 }} src={User3} />
    </AvatarGroup>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default GroupedSizeCode;
