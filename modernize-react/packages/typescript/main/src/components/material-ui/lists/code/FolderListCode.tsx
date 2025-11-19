import CodeDialog from 'src/components/shared/CodeDialog';
const FolderListCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { 
List, 
ListItem, 
ListItemText, 
ListItemAvatar, 
Avatar,
Card
} from '@mui/material';

import { 
IconPhoto, 
IconBriefcase, 
IconBeach 
} from '@tabler/icons-react';

<Card>
    <List>
        <ListItem>
            <ListItemAvatar>
              <Avatar>
                <IconPhoto width={20} height={20} />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary="Photos" secondary="Jan 9, 2014" />
        </ListItem>
        <ListItem>
            <ListItemAvatar>
              <Avatar>
                <IconBriefcase width={20} height={20} />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary="Work" secondary="Jan 7, 2014" />
        </ListItem>
        <ListItem>
            <ListItemAvatar>
              <Avatar>
                <IconBeach width={20} height={20} />
              </Avatar>
            </ListItemAvatar>
            <ListItemText primary="Vacation" secondary="July 20, 2014" />
        </ListItem>
    </List>
</Card>`}
      </CodeDialog>
    </>
  );
};

export default FolderListCode;
