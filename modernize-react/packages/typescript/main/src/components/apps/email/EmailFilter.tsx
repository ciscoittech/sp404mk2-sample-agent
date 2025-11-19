// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';

import {
  ListItemText,
  ListItemButton,
  List,
  Divider,
  ListItemIcon,
  Box,
  Typography,
} from '@mui/material';

import { EmailContext } from "src/context/EmailContext";
import EmailCompose from './EmailCompose';
import Scrollbar from 'src/components/custom-scroll/Scrollbar';
import {
  IconMail,
  IconSend,
  IconFlag,
  IconTrash,
  IconStar,
  IconAlertCircle,
  IconFolder,
  IconNote,
} from '@tabler/icons-react';
import { GeneralIcon } from 'src/types/apps/icon';
import { CustomizerContext } from 'src/context/CustomizerContext';

interface fitlerType {
  id?: number;
  filterbyTitle?: string;
  icon?: GeneralIcon | any;
  name?: string;
  divider?: boolean;
  color?: string;
}

const EmailFilter = () => {

  const { isBorderRadius } = useContext(CustomizerContext);
  const br = `${isBorderRadius}px`;

  const { setFilter, filter } = useContext(EmailContext);

  const handleFilterClick = (filterName: string | any) => {
    setFilter(filterName);
  };

  const filterData: fitlerType[] = [
    {
      id: 2,
      name: 'inbox',
      icon: IconMail,
      color: 'inherit',
    },
    {
      id: 3,
      name: 'sent',
      icon: IconSend,
      color: 'inherit',
    },
    {
      id: 4,
      name: 'draft',
      icon: IconNote,
      color: 'inherit',
    },
    {
      id: 4,
      name: 'spam',
      icon: IconFlag,
      color: 'inherit',
    },
    {
      id: 5,
      name: 'trash',
      icon: IconTrash,
      color: 'inherit',
    },
    {
      id: 6,
      divider: true,
    },
    {
      id: 1,
      filterbyTitle: 'Sort By',
    },
    {
      id: 7,
      name: 'starred',
      icon: IconStar,
      color: 'inherit',
    },
    {
      id: 8,
      name: 'important',
      icon: IconAlertCircle,
      color: 'inherit',
    },
    {
      id: 9,
      divider: true,
    },
    {
      id: 13,
      filterbyTitle: 'Labels',
    },
    {
      id: 10,
      name: 'Promotional',
      icon: IconFolder,
      color: 'primary.main',
    },
    {
      id: 11,
      name: 'Social',
      icon: IconFolder,
      color: 'error.main',
    },
    {
      id: 12,
      name: 'Health',
      icon: IconFolder,
      color: 'success.main',
    },
  ];

  return (
    <>
      <Box>
        {/* ------------------------------------------- */}
        {/* Email compose */}
        {/* ------------------------------------------- */}
        <EmailCompose />
      </Box>
      <List>
        <Scrollbar sx={{ height: { lg: 'calc(100vh - 100px)', md: '100vh' }, maxHeight: '800px' }}>
          {filterData.map((item) => {
            if (item.filterbyTitle) {
              return (
                <Typography
                  variant="subtitle2"
                  p={3}
                  pb={1}
                  pl={5.5}
                  fontWeight={600}
                  key={item.id}
                >
                  {item.filterbyTitle}
                </Typography>
              );
            } else if (item.divider) {
              return <Divider key={item.id} />;
            }

            return (
              <ListItemButton
                sx={{
                  mb: 1,
                  px: '20px',
                  mx: 3,
                  borderRadius: br,
                }}
                selected={filter === `${item.name}`}
                onClick={() => handleFilterClick(item.name)}
                key={`${item.id}${item.name}`}
              >
                {/* ------------------------------------------- */}
                {/* If list to filter */}
                {/* ------------------------------------------- */}
                <ListItemIcon sx={{ minWidth: '30px', color: item.color }}>
                  <item.icon stroke="1.5" size={19} />
                </ListItemIcon>
                <ListItemText sx={{ textTransform: 'capitalize' }}>{item.name}</ListItemText>
              </ListItemButton>
            );
          })}
        </Scrollbar>
      </List>
    </>
  );
};

export default EmailFilter;
