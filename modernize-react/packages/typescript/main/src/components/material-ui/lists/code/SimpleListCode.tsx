import CodeDialog from 'src/components/shared/CodeDialog';
const SimpleListCode = () => {
  return (
    <>
      <CodeDialog>
        {`

import React from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Card
} from '@mui/material';

import { IconInbox, IconMailOpened } from '@tabler/icons-react';

<Card>
    <List>
        <ListItem disablePadding>
            <ListItemButton>
                <ListItemIcon>
                    <IconInbox width={20} height={20} />
                </ListItemIcon>
                <ListItemText primary="Inbox" />
            </ListItemButton>
            </ListItem>
            <ListItem disablePadding>
            <ListItemButton>
                <ListItemIcon>
                    <IconMailOpened width={20} height={20} />
                </ListItemIcon>
                <ListItemText primary="Drafts" />
            </ListItemButton>
        </ListItem>
    </List>
    <Divider />
    <List>
        <ListItem disablePadding>
            <ListItemButton>
              <ListItemText primary="Trash" />
            </ListItemButton>
        </ListItem>
        <ListItem disablePadding>
            <ListItemButton component="a" href="#simple-list">
              <ListItemText primary="Spam" />
            </ListItemButton>
        </ListItem>
    </List>
</Card>`}
      </CodeDialog>
    </>
  );
};

export default SimpleListCode;
