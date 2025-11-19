import React from 'react';
import icon1 from 'src/assets/images/svgs/google-icon.svg';
import icon2 from 'src/assets/images/svgs/github-icon.svg';
import CustomSocialButton from '../../../components/forms/theme-elements/CustomSocialButton';
import { Avatar, Box, Stack } from '@mui/material';

import { AuthContext } from 'src/guards/auth/AuthContext';
import { useContext } from 'react';


const AuthSocialButtons = ({ title }) => {
  const { loginWithProvider } = useContext(AuthContext);

  const handleGoogle = async () => {
    try {
      await loginWithProvider("google");
    } catch (error) {
      console.error("Google login failed", error);
    }
  };

  const handleGithub = async () => {
    try {
      await loginWithProvider("github");
    } catch (error) {
      console.error("GitHub login failed", error);
    }
  };

  return (
    <>
      <Stack direction="row" justifyContent="center" spacing={2} mt={3}>
        <CustomSocialButton onClick={handleGoogle}>
          <Avatar
            src={icon1}
            alt={icon1}
            sx={{
              width: 16,
              height: 16,
              borderRadius: 0,
              mr: 1,
            }}
          />
          <Box
            sx={{ display: { xs: 'none', sm: 'flex' }, whiteSpace: 'nowrap', mr: { sm: '3px' } }}
          >
            {title}
          </Box>{' '}
          Google
        </CustomSocialButton>
        <CustomSocialButton onClick={handleGithub}>
          <Avatar
            src={icon2}
            alt={icon2}
            sx={{
              width: 21,
              height: 21,
              borderRadius: 0,
              mr: 1,
            }}
          />
          <Box
            sx={{ display: { xs: 'none', sm: 'flex' }, whiteSpace: 'nowrap', mr: { sm: '3px' } }}
          >
            {title}
          </Box>{' '}
          Github
        </CustomSocialButton>
      </Stack>
    </>
  );
};
export default AuthSocialButtons;
