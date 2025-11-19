import CodeDialog from '../../../shared/CodeDialog';

const GroupedCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { Avatar, AvatarGroup, Stack } from '@mui/material';
import { IconMoodSmile } from '@tabler/icons';


<Stack direction="row" spacing={1} justifyContent="center">
    <AvatarGroup max={4}>
        <Avatar alt="Remy Sharp" src={User1} />
        <Avatar alt="Travis Howard" src={User2} />
        <Avatar alt="Cindy Baker" src={User3} />
    </AvatarGroup>
</Stack>`}
      </CodeDialog>
    </>
  );
};

export default GroupedCode;
