import { useMediaQuery, Box, Drawer, Container } from '@mui/material';
import NavListing from './NavListing/NavListing';
import Logo from '../../shared/logo/Logo';
import { useContext } from 'react';
import { CustomizerContext } from 'src/context/CustomizerContext';
import config from 'src/context/config';
import SidebarItems from '../../vertical/sidebar/SidebarItems';

const Navigation = () => {
  const lgUp = useMediaQuery((theme) => theme.breakpoints.up('lg'));
  const { isLayout, isMobileSidebar, setIsMobileSidebar } = useContext(CustomizerContext);
  const SidebarWidth = config.SidebarWidth

  if (lgUp) {
    return (
      <Box sx={{ borderBottom: '1px solid rgba(0,0,0,0.05)' }} py={2}>
        {/* ------------------------------------------- */}
        {/* Sidebar for desktop */}
        {/* ------------------------------------------- */}
        <Container
          sx={{
            maxWidth: isLayout === 'boxed' ? 'lg' : '100%!important',
          }}
        >
          <NavListing />
        </Container>
      </Box>
    );
  }

  return (
    (<Drawer
      anchor="left"
      open={isMobileSidebar}
      onClose={() => setIsMobileSidebar(false)}
      variant="temporary"
      slotProps={{
        paper: {
          sx: {
            width: SidebarWidth,
            border: '0 !important',
            boxShadow: (theme) => theme.shadows[8],
          },
        }
      }}
    >
      {/* ------------------------------------------- */}
      {/* Logo */}
      {/* ------------------------------------------- */}
      <Box px={2}>
        <Logo />
      </Box>
      {/* ------------------------------------------- */}
      {/* Sidebar For Mobile */}
      {/* ------------------------------------------- */}
      <SidebarItems />
    </Drawer>)
  );
};

export default Navigation;
