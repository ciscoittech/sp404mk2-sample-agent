import CodeDialog from 'src/components/shared/CodeDialog';
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
  Card
} from '@mui/material';

import { 
  IconWifi, 
  IconBluetooth 
} from '@tabler/icons-react';

import CustomSwitch from '../../forms/theme-elements/CustomSwitch';

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

<Card>
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
              inputProps={{
                'aria-labelledby': 'switch-list-label-wifi',
              }}
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
              inputProps={{
                'aria-labelledby': 'switch-list-label-bluetooth',
              }}
            />
        </ListItem>
    </List>
</Card>`}
      </CodeDialog>
    </>
  );
};

export default SwitchListCode;
