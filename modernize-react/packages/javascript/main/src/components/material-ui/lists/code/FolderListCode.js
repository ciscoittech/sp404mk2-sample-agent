import CodeDialog from '../../../shared/CodeDialog';

const FolderListCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import { 
List, 
ListItem, 
ListItemText, 
ListItemAvatar, 
Avatar,
Paper
} from '@mui/material';

import { 
IconPhoto, 
IconBriefcase, 
IconBeach 
} from '@tabler/icons';

<Paper variant="outlined">
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
</Paper>`}
      </CodeDialog>
    </>
  );
};

export default FolderListCode;
