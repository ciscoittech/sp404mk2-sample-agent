import CodeDialog from '../../../shared/CodeDialog';

const SizesCode = () => {
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
    <Chip label="Small" size="small" color="primary" />
    <Chip label="Normal" color="primary" />
</Card>`}
      </CodeDialog>
    </>
  );
};

export default SizesCode;
