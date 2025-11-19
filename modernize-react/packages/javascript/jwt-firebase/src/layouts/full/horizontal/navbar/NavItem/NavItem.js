// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';


// mui imports
import { ListItemIcon, List, styled, ListItemText, useTheme, ListItemButton } from '@mui/material';
import { CustomizerContext } from 'src/context/CustomizerContext';



const NavItem = ({ item, level, pathDirect, onClick }) => {

  const { isBorderRadius } = useContext(CustomizerContext);

  const Icon = item.icon;
  const theme = useTheme();
  const itemIcon =
    level > 1 ? <Icon stroke={1.5} size="1rem" /> : <Icon stroke={1.5} size="1.1rem" />;

  const ListItemStyled2 = styled(ListItemButton)(() => ({
    padding: '5px 10px',
    gap: '10px',
    borderRadius: `${isBorderRadius}px`,
    marginBottom: level > 1 ? '3px' : '0px',
    color:
      level > 1 && pathDirect === item.href ? `${theme.palette.primary.main}!important` : theme.palette.text.secondary,

    '&:hover': {
      backgroundColor: theme.palette.primary.light,
    },
    '&.Mui-selected': {
      color: level > 1 ? theme.palette.primary.main : 'white!important',
      backgroundColor: level > 1 ? 'transparent' : theme.palette.primary.main,
      '&:hover': {
        backgroundColor: level > 1 ? '' : theme.palette.primary.main,
        color: 'white',
      },
    },
  }));



  return (
    <List component="li" disablePadding key={item.id}>
      <ListItemStyled2
        disabled={item.disabled}
        selected={pathDirect === item.href}
        onClick={onClick}
      >
        <ListItemIcon
          sx={{
            minWidth: 'auto',
            p: '3px 0',
            color: 'inherit',
          }}
        >
          {itemIcon}
        </ListItemIcon>
        <ListItemText>{item.title}</ListItemText>
      </ListItemStyled2>
    </List>
  );
};


export default NavItem;
