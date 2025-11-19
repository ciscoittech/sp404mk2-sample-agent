import CodeDialog from 'src/components/shared/CodeDialog';
const CustomIconCode = () => {
  return (
    <>
      <CodeDialog>
        {`

import React from 'react';
import { 
Avatar, 
Chip, 
 }  from '@mui/material';
import { 
IconCheck, 
IconChecks } from '@tabler/icons-react';
import InlineItemCard from "@/app/components/shared/InlineItemCard";

<InlineItemCard>
    <Chip
        label="Custom Icon" color="primary" avatar={<Avatar >M</Avatar>}
        onDelete={handleDelete}
        deleteIcon={<IconCheck width={20} />}
    />
    <Chip
        label="Custom Icon" color="secondary" avatar={<Avatar >S</Avatar>}
        onDelete={handleDelete}
        deleteIcon={<IconChecks width={20} />}
    />
</InlineItemCard>`}
      </CodeDialog>
    </>
  );
};

export default CustomIconCode;
