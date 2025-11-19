import CodeDialog from 'src/components/shared/CodeDialog';
const DisabledCode = () => {
  return (
    <>
      <CodeDialog>
        {`

import React from 'react';
import { 
Avatar, 
Chip, 
}  from '@mui/material';
import { IconMoodHappy } from '@tabler/icons-react';
import InlineItemCard from "@/app/components/shared/InlineItemCard";

<InlineItemCard>
    <Chip
        label="Custom Icon" disabled avatar={<Avatar >M</Avatar>}
        onDelete={handleDelete}
    />
    <Chip
        label="Custom Icon" color="primary" disabled avatar={<Avatar >S</Avatar>}
        onDelete={handleDelete}
    />
</InlineItemCard>`}
      </CodeDialog>
    </>
  );
};

export default DisabledCode;
