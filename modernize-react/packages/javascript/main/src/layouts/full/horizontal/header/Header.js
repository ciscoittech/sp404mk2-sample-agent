import * as React from 'react';
import { IconButton, Box, AppBar, useMediaQuery, Toolbar, styled, Stack } from '@mui/material';
import PropTypes from 'prop-types';
import { IconMenu2, IconMoon, IconSun } from '@tabler/icons';
import Notifications from 'src/layouts/full/vertical/header/Notifications';
import Cart from 'src/layouts/full/vertical/header/Cart';
import Profile from 'src/layouts/full/vertical/header/Profile';
import Search from 'src/layouts/full/vertical/header/Search';
import Language from 'src/layouts/full/vertical/header/Language';
import Navigation from 'src/layouts/full/vertical/header/Navigation';
import Logo from 'src/layouts/full/shared/logo/Logo';
import config from 'src/context/config';
import { CustomizerContext } from 'src/context/CustomizerContext';
import { ProductProvider } from 'src/context/EcommerceContext/index'

const Header = () => {
  const lgDown = useMediaQuery((theme) => theme.breakpoints.down('lg'));
  const lgUp = useMediaQuery((theme) => theme.breakpoints.up('lg'));

  const { isLayout, setIsMobileSidebar, isMobileSidebar, activeMode, setActiveMode } = React.useContext(CustomizerContext);
  const TopbarHeight = config.topbarHeight;


  const AppBarStyled = styled(AppBar)(({ theme }) => ({
    background: theme.palette.background.paper,
    justifyContent: 'center',
    backdropFilter: 'blur(4px)',

    [theme.breakpoints.up('lg')]: {
      minHeight: TopbarHeight,
    },
  }));
  const ToolbarStyled = styled(Toolbar)(({ theme }) => ({
    margin: '0 auto',
    width: '100%',
    color: `${theme.palette.text.secondary} !important`,
  }));

  return (
    <ProductProvider>
      <AppBarStyled position="sticky" color="default" elevation={8}>
        <ToolbarStyled
          sx={{
            maxWidth: isLayout === 'boxed' ? 'lg' : '100%!important',
          }}
        >
          <Box sx={{ width: lgDown ? '45px' : 'auto', overflow: 'hidden' }}>
            <Logo />
          </Box>
          {/* ------------------------------------------- */}
          {/* Toggle Button Sidebar */}
          {/* ------------------------------------------- */}
          {lgDown ? (
            <IconButton
              color="inherit"
              aria-label="menu"
              onClick={() => setIsMobileSidebar(!isMobileSidebar)}
            >
              <IconMenu2 />
            </IconButton>
          ) : (
            ''
          )}
          {/* ------------------------------------------- */}
          {/* Search Dropdown */}
          {/* ------------------------------------------- */}
          <Search />
          {lgUp ? (
            <>
              <Navigation />
            </>
          ) : null}
          <Box flexGrow={1} />
          <Stack spacing={1} direction="row" alignItems="center">
            <Language />
            {/* ------------------------------------------- */}
            {/* Ecommerce Dropdown */}
            {/* ------------------------------------------- */}
            <Cart />
            {/* ------------------------------------------- */}
            {/* End Ecommerce Dropdown */}
            {/* ------------------------------------------- */}

            <IconButton size="large" color="inherit">
              {activeMode === 'light' ? (
                <IconMoon size="21" stroke="1.5" onClick={() => setActiveMode("dark")} />
              ) : (
                <IconSun size="21" stroke="1.5" onClick={() => setActiveMode("light")} />
              )}
            </IconButton>

            <Notifications />
            <Profile />
          </Stack>
        </ToolbarStyled>
      </AppBarStyled>
    </ProductProvider>
  );
};

Header.propTypes = {
  sx: PropTypes.object,
  toggleSidebar: PropTypes.func,
};

export default Header;
