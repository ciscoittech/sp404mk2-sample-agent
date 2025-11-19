import CodeDialog from '../../../shared/CodeDialog';

const CustomOutlinedIcon = () => {
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
      label="Custom Icon"
      variant="outlined"
      color="primary"
      avatar={<Avatar>M</Avatar>}
      onDelete={handleDelete}
      deleteIcon={<IconCheck width={20} />}
    />
    <Chip
      label="Custom Icon"
      variant="outlined"
      color="secondary"
      avatar={<Avatar>S</Avatar>}
      onDelete={handleDelete}
      deleteIcon={<IconChecks width={20} />}
    />
</Card>`}
      </CodeDialog>
    </>
  );
};

export default CustomOutlinedIcon;
