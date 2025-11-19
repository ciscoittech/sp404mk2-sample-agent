import CodeDialog from '../../../shared/CodeDialog';

const SwitchListCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  ListSubheader,
  Paper
} from '@mui/material';

import { 
  IconWifi, 
  IconBluetooth 
} from '@tabler/icons';

const label = { inputProps: { 'aria-label': 'Switch demo' } };

const [checked, setChecked] = React.useState(['wifi']);

const handleToggle = (value: string) => () => {
    const currentIndex = checked.indexOf(value);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(value);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
};

<Paper variant="outlined">
    <List subheader={<ListSubheader>Settings</ListSubheader>}>
        <ListItem>
            <ListItemIcon>
              <IconWifi width={20} height={20} />
            </ListItemIcon>
            <ListItemText id="switch-list-label-wifi" primary="Wi-Fi" />
            <CustomSwitch
              edge="end"
              onChange={handleToggle('wifi')}
              checked={checked.indexOf('wifi') !== -1}
              {...label}
            />
        </ListItem>
        <ListItem>
            <ListItemIcon>
              <IconBluetooth width={20} height={20} />
            </ListItemIcon>
            <ListItemText id="switch-list-label-bluetooth" primary="Bluetooth" />
            <CustomSwitch
              edge="end"
              onChange={handleToggle('bluetooth')}
              checked={checked.indexOf('bluetooth') !== -1}
              {...label}
            />
        </ListItem>
    </List>
</Paper>`}
      </CodeDialog>
    </>
  );
};

export default SwitchListCode;
