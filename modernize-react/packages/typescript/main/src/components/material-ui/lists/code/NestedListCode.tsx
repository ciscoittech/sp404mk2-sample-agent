import CodeDialog from 'src/components/shared/CodeDialog';
const NestedListCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import {
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader,
  Collapse,
  Card
} from '@mui/material';

import {
  IconInbox,
  IconMailOpened,
  IconSend,
  IconChevronDown,
  IconChevronUp,
  IconStar,
} from '@tabler/icons-react';

const [open, setOpen] = React.useState(true);

const handleClick = () => {
    setOpen(!open);
};

<Card>
    <List
    component="nav"
    aria-labelledby="nested-list-subheader"
    subheader={
        <ListSubheader component="div" id="nested-list-subheader">
              Nested List Items
        </ListSubheader>
          }
    >
        <ListItemButton>
            <ListItemIcon>
              <IconSend width={20} height={20} />
            </ListItemIcon>
            <ListItemText primary="Sent mail" />
        </ListItemButton>
        <ListItemButton>
            <ListItemIcon>
              <IconMailOpened width={20} height={20} />
            </ListItemIcon>
            <ListItemText primary="Drafts" />
        </ListItemButton>
        <ListItemButton onClick={handleClick}>
            <ListItemIcon>
              <IconInbox width={20} height={20} />
            </ListItemIcon>
            <ListItemText primary="Inbox" />
            {open ? <IconChevronUp /> : <IconChevronDown />}
        </ListItemButton>
        <Collapse in={open} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              <ListItemButton sx={{ pl: 4 }}>
                <ListItemIcon>
                  <IconStar width={20} height={20} />
                </ListItemIcon>
                <ListItemText primary="Starred" />
              </ListItemButton>
            </List>
        </Collapse>
    </List>
</Card>`}
      </CodeDialog>
    </>
  );
};

export default NestedListCode;
