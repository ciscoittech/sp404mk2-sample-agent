import CodeDialog from '../../../shared/CodeDialog';

const OutlinedCode = () => {
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

import { IconMoodHappy } from '@tabler/icons';


<Card>
    <Chip variant="outlined" avatar={<Avatar>M</Avatar>} label="Default Filled" />
    <Chip
      variant="outlined"
      avatar={<Avatar>M</Avatar>}
      label="Default Deletable"
      onDelete={handleDelete}
    />
    <Chip
      variant="outlined"
      avatar={<Avatar alt="Natacha" src={User1} />}
      label="Default Filled"
      color="primary"
    />
    <Chip
      variant="outlined"
      avatar={<Avatar alt="Natacha" src={User1} />}
      label="Default Deletable"
      color="primary"
      onDelete={handleDelete}
    />
    <Chip
      variant="outlined"
      icon={<IconMoodHappy />}
      label="Default Filled"
      color="secondary"
    />
    <Chip
      variant="outlined"
      icon={<IconMoodHappy />}
      label="Default Deletable"
      color="secondary"
      onDelete={handleDelete}
    />
    <Chip
      variant="outlined"
      avatar={<Avatar alt="Natacha" src={User2} />}
      label="Default Filled"
      color="success"
    />
    <Chip
      variant="outlined"
      avatar={<Avatar alt="Natacha" src={User2} />}
      label="Default Deletable"
      color="success"
      onDelete={handleDelete}
    />
    <Chip
      variant="outlined"
      icon={<IconMoodHappy />}
      label="Default Filled"
      color="warning"
    />
    <Chip
      variant="outlined"
      icon={<IconMoodHappy />}
      label="Default Deletable"
      color="warning"
      onDelete={handleDelete}
    />
    <Chip
      variant="outlined"
      avatar={<Avatar alt="Natacha" src={User3} />}
      label="Default Filled"
      color="error"
    />
    <Chip
      variant="outlined"
      avatar={<Avatar alt="Natacha" src={User3} />}
      label="Default Deletable"
      color="error"
      onDelete={handleDelete}
    />
</Card>`}
      </CodeDialog>
    </>
  );
};

export default OutlinedCode;
