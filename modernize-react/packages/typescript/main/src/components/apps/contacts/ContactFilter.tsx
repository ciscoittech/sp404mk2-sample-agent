// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext } from 'react';

import {
  ListItemText,
  ListItemButton,
  List,
  Divider,
  ListItemIcon,
  Typography,
} from '@mui/material';

import Scrollbar from 'src/components/custom-scroll/Scrollbar';
import { IconMail, IconSend, IconBucket, IconFolder } from '@tabler/icons-react';
import ContactAdd from './ContactAdd';
import { ContactContext } from "src/context/ConatactContext";
import { CustomizerContext } from 'src/context/CustomizerContext';

interface DataType {
  id: number;
  name?: string;
  sort?: string;
  icon?: any;
  filterbyTitle?: string;
  devider?: boolean;
  color?: string;
}

const ContactFilter = () => {

  const { isBorderRadius } = useContext(CustomizerContext);
  const br = `${isBorderRadius}px`;

  const { setSelectedDepartment, updateSearchTerm, selectedDepartment } = useContext(ContactContext);

  const filterData: DataType[] = [
    {
      id: 2,
      name: 'All',
      sort: 'show_all',
      icon: IconMail,
    },
    {
      id: 3,
      name: 'Frequent',
      sort: 'frequent_contact',
      icon: IconSend,
    },
    {
      id: 4,
      name: 'Starred',
      sort: 'starred_contact',
      icon: IconBucket,
    },
    {
      id: 6,
      devider: true,
    },
    {
      id: 5,
      filterbyTitle: 'Categories',
    },

    {
      id: 7,
      name: 'Engineering',
      sort: 'engineering_department',
      icon: IconFolder,
      color: 'primary.main',
    },
    {
      id: 8,
      name: 'Support',
      sort: 'support_department',
      icon: IconFolder,
      color: 'error.main',
    },
    {
      id: 9,
      name: 'Sales',
      sort: 'sales_department',
      icon: IconFolder,
      color: 'success.main',
    },
  ];

  const handleDepartmentClick = (department: string) => {
    setSelectedDepartment(department);
    updateSearchTerm("");
  };


  return (
    <>
      <ContactAdd />
      <List>
        <Scrollbar sx={{ height: { lg: 'calc(100vh - 100px)', md: '100vh' }, maxHeight: '800px' }}>
          {filterData.map((filter) => {
            if (filter.filterbyTitle) {
              return (
                <Typography
                  variant="subtitle1"
                  fontWeight={600}
                  pl={5.1}
                  mt={1}
                  pb={2}
                  key={filter.id}
                >
                  {filter.filterbyTitle}
                </Typography>
              );
            } else if (filter.devider) {
              return <Divider key={filter.id} sx={{ mb: 3 }} />;
            }

            return (
              <ListItemButton
                sx={{ mb: 1, mx: 3, borderRadius: br }}
                selected={selectedDepartment === `${filter.name}`}

                onClick={() => handleDepartmentClick(filter.name || '')}
                key={filter.id}
              >
                <ListItemIcon sx={{ minWidth: '30px', color: filter.color }}>
                  <filter.icon stroke="1.5" size={19} />
                </ListItemIcon>
                <ListItemText>{filter.name}</ListItemText>
              </ListItemButton>
            );
          })}
        </Scrollbar>
      </List>
    </>
  );
};

export default ContactFilter;