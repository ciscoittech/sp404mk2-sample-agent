import CodeDialog from 'src/components/shared/CodeDialog';
const ControlsListCode = () => {
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
  IconButton,
  Checkbox,
  Card
} from '@mui/material';

import { IconMessage } from '@tabler/icons-react';

const [checked, setChecked] = React.useState([0]);

const handleToggle = (value: number) => () => {
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
    <List>
        {[0, 1, 2, 3].map((value) => {
            const labelId = 'checkbox-list-label-{value}';

            return (
                <ListItem
                    key={value}
                    secondaryAction={
                        <IconButton edge="end" aria-label="comments">
                            <IconMessage width={20} height={20} />
                        </IconButton>
                    }
                    disablePadding
                >
                    <ListItemButton role={undefined} onClick={handleToggle(value)} dense>
                        <ListItemIcon>
                            <Checkbox
                                checked={checked.indexOf(value) !== -1}
                                tabIndex={-1}
                                disableRipple
                                inputProps={{ 'aria-labelledby': labelId }}
                                edge="start"
                            />
                        </ListItemIcon>
                        <ListItemText id={labelId} primary={'Line item {value + 1}'} />
                    </ListItemButton>
                </ListItem>
            );
        })}
    </List>
</Card > `}
      </CodeDialog>
    </>
  );
};

export default ControlsListCode;
