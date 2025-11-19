import CodeDialog from '../../../shared/CodeDialog';

const CustomIconCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { 
Avatar, 
Chip,
Card
}  from '@mui/material';

import { 
IconCheck, 
IconChecks } from '@tabler/icons';

<Card>
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
</Card>`}
      </CodeDialog>
    </>
  );
};

export default CustomIconCode;
