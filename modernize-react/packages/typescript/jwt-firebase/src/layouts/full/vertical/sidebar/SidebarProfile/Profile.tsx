import { Box, Avatar, Typography, IconButton, Tooltip, useMediaQuery } from '@mui/material';
import img1 from 'src/assets/images/profile/user-1.jpg';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { IconPower } from '@tabler/icons-react';

import { useNavigate } from "react-router";

import { CustomizerContext } from 'src/context/CustomizerContext';
import { useContext } from 'react';

import { AuthContext } from 'src/guards/auth/AuthContext'

export const Profile = () => {
  const { isSidebarHover, isCollapse } = useContext(CustomizerContext);

  const lgUp = useMediaQuery((theme: any) => theme.breakpoints.up('lg'));
  const hideMenu = lgUp ? isCollapse == 'mini-sidebar' && !isSidebarHover : '';



  const navigate = useNavigate();


  const { logout, user }: any = useContext(AuthContext);

  const userName = user?.displayName || "Mathew";


  const handleLogout = async () => {

    logout()
    navigate('/auth/login');
  };

  return (
    <Box
      display={'flex'}
      alignItems="center"
      gap={2}
      sx={{ m: 3, p: 2, bgcolor: `${'secondary.light'}` }}
    >
      {!hideMenu ? (
        <>
          <Avatar alt="Remy Sharp" src={img1} />

          <Box>
            <Typography variant="h6">{userName}</Typography>
            <Typography variant="caption">Designer</Typography>
          </Box>
          <Box sx={{ ml: 'auto' }}>
            <Tooltip title="Logout" placement="top">
              <IconButton color="primary" aria-label="logout" size="small" onClick={handleLogout}>
                <IconPower size="20" />
              </IconButton>
            </Tooltip>
          </Box>
        </>
      ) : (
        ''
      )}
    </Box>
  );
};
