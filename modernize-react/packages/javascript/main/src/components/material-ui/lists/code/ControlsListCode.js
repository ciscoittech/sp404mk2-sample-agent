import CodeDialog from '../../../shared/CodeDialog';

const ControlsListCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from "react";
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Checkbox,
  Paper
} from '@mui/material';

import { IconMessage } from '@tabler/icons';
import BlankCard from '../../shared/BlankCard';

const [checked, setChecked] = React.useState([0]);

const handleToggle = (valueNestedListCode) => () => {
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
    <List>
                    {[0, 1, 2, 3].map((value) => {
                        const labelId = checkbox-list-label-{value};

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
                                        <CustomCheckbox
                                            edge="start"
                                            checked={checked.indexOf(value) !== -1}
                                            tabIndex={-1}
                                            disableRipple
                                        />
                                    </ListItemIcon>
                                    <ListItemText id={labelId} primary={Line item {value + 1}} />
                                </ListItemButton>
                            </ListItem>
                        );
                    })}
                </List>
</Paper > `}
      </CodeDialog>
    </>
  );
};

export default ControlsListCode;
