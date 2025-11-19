import CodeDialog from '../../../shared/CodeDialog';

const FilledCode = () => {
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
    <Chip avatar={<Avatar>M</Avatar>} label="Default Filled" />
    <Chip
    avatar={<Avatar>M</Avatar>}
    label="Default Deletable"
    onDelete={handleDelete}
    />
    <Chip
    avatar={<Avatar alt="Natacha" src={User1} />}
    label="Primary Filled"
    color="primary"
    />
    <Chip
    avatar={<Avatar alt="Natacha" src={User1} />}
    label="Primary Deletable"
    color="primary"
    onDelete={handleDelete}
    />
    <Chip icon={<IconMoodHappy />} label="Secondary Filled" color="secondary" />
    <Chip
    icon={<IconMoodHappy />}
    label="Secondary Deletable"
    color="secondary"
    onDelete={handleDelete}
    />
    <Chip
    avatar={<Avatar alt="Natacha" src={User2} />}
    label="Default Filled"
    color="success"
    />
    <Chip
    avatar={<Avatar alt="Natacha" src={User2} />}
    label="Default Deletable"
    color="success"
    onDelete={handleDelete}
    />
    <Chip icon={<IconMoodHappy />} label="Default Filled" color="warning" />
    <Chip
    icon={<IconMoodHappy />}
    label="Default Deletable"
    color="warning"
    onDelete={handleDelete}
    />
    <Chip
    avatar={<Avatar alt="Natacha" src={User3} />}
    label="Default Filled"
    color="error"
    />
    <Chip
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

export default FilledCode;
