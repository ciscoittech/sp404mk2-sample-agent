import CodeDialog from '../../../shared/CodeDialog';

const DisabledCode = () => {
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

<Card>
    <Chip
        label="Custom Icon" disabled avatar={<Avatar >M</Avatar>}
        onDelete={handleDelete}
    />
    <Chip
        label="Custom Icon" color="primary" disabled avatar={<Avatar >S</Avatar>}
        onDelete={handleDelete}
    />
</Card>`}
      </CodeDialog>
    </>
  );
};

export default DisabledCode;
