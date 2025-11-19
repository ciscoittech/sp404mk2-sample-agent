// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useState } from 'react';
import { Button, Box, Drawer, useMediaQuery, Theme } from '@mui/material';
import PageContainer from 'src/components/container/PageContainer';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import ContactDetails from 'src/components/apps/contacts/ContactDetails';
import ContactList from 'src/components/apps/contacts/ContactList';
import ContactSearch from 'src/components/apps/contacts/ContactSearch';
import ContactFilter from 'src/components/apps/contacts/ContactFilter';
import AppCard from 'src/components/shared/AppCard';
import { ContactContextProvider } from 'src/context/ConatactContext';

const drawerWidth = 240;
const secdrawerWidth = 320;

const Contacts = () => {
  const [isLeftSidebarOpen, setLeftSidebarOpen] = useState(false);
  const [isRightSidebarOpen, setRightSidebarOpen] = useState(false);
  const lgUp = useMediaQuery((theme: Theme) => theme.breakpoints.up('lg'));
  const mdUp = useMediaQuery((theme: Theme) => theme.breakpoints.up('md'));

  const BCrumb = [
    {
      to: '/',
      title: 'Home',
    },
    {
      title: 'Contact',
    },
  ];


  
  return (

    <ContactContextProvider>
      <PageContainer title="Contact App" description="this is Contact page">
        <Breadcrumb title="Contact app" items={BCrumb} />
        <AppCard>
          {/* ------------------------------------------- */}
          {/* Left Part */}
          {/* ------------------------------------------- */}


          <Drawer
            open={isLeftSidebarOpen}
            onClose={() => setLeftSidebarOpen(false)}
            sx={{
              width: drawerWidth,
              [`& .MuiDrawer-paper`]: { width: drawerWidth, position: 'relative', zIndex: 2 },
              flexShrink: 0,
            }}
            variant={lgUp ? 'permanent' : 'temporary'}
          >
            <ContactFilter />
          </Drawer>
          {/* ------------------------------------------- */}
          {/* Middle part */}
          {/* ------------------------------------------- */}
          <Box
            sx={{
              minWidth: secdrawerWidth,
              width: { xs: '100%', md: secdrawerWidth, lg: secdrawerWidth },
              flexShrink: 0,
            }}
          >
            <ContactSearch onClick={() => setLeftSidebarOpen(true)} />
            <ContactList showrightSidebar={() => setRightSidebarOpen(true)} />
          </Box>
          {/* ------------------------------------------- */}
          {/* Right part */}
          {/* ------------------------------------------- */}
          <Drawer
            anchor="right"
            open={isRightSidebarOpen}
            onClose={() => setRightSidebarOpen(false)}
            variant={mdUp ? 'permanent' : 'temporary'}
            sx={{
              width: mdUp ? secdrawerWidth : '100%',
              zIndex: lgUp ? 0 : 1,
              flex: mdUp ? 'auto' : '',
              [`& .MuiDrawer-paper`]: { width: '100%', position: 'relative' },
            }}
          >
            {/* back btn Part */}
            {mdUp ? (
              ''
            ) : (
              <Box sx={{ p: 3 }}>
                <Button
                  variant="outlined"
                  color="primary"
                  size="small"
                  onClick={() => setRightSidebarOpen(false)}
                  sx={{ mb: 3, display: { xs: 'block', md: 'none', lg: 'none' } }}
                >
                  Back{' '}
                </Button>
              </Box>
            )}
            <ContactDetails />
          </Drawer>
        </AppCard>
      </PageContainer>
    </ContactContextProvider >
  );
};

export default Contacts;
