import React from 'react';
import { Box, Typography, Button, Divider, Alert, Stack } from '@mui/material';
import { useNavigate } from 'react-router';

import { useContext, useState } from "react";
import { AuthContext } from "src/guards/auth/AuthContext";

import CustomTextField from '../../../components/forms/theme-elements/CustomTextField';
import CustomFormLabel from '../../../components/forms/theme-elements/CustomFormLabel';
import AuthSocialButtons from './AuthSocialButtons';


const AuthRegister = ({ title, subtitle, subtext }) => {
  const [email, setEmail] = useState("");
  const [userName, setuserName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);

  let navigate = useNavigate();
  const { signup } = useContext(AuthContext);

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      await signup(email, password, userName);
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  };


  return (
    <>
      {title ? (
        <Typography fontWeight="700" variant="h3" mb={1}>
          {title}
        </Typography>
      ) : null}

      {subtext}
      <AuthSocialButtons title="Sign up with" />

      <Box mt={3}>
        <Divider>
          <Typography
            component="span"
            color="textSecondary"
            variant="h6"
            fontWeight="400"
            position="relative"
            px={2}
          >
            or sign up with
          </Typography>
        </Divider>
      </Box>

      <Box>
        {error && <Alert severity="error">{error}</Alert>}

        <form onSubmit={handleRegister}>
          <Stack mb={3}>
            <CustomFormLabel htmlFor="username">User Name</CustomFormLabel>
            <CustomTextField
              id="username"
              variant="outlined"
              fullWidth
              value={userName}
              onChange={(e) =>
                setuserName(e.target.value)
              }
            />
            <CustomFormLabel htmlFor="email">Email Address</CustomFormLabel>
            <CustomTextField
              id="email"
              variant="outlined"
              fullWidth
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
            />
            <CustomFormLabel htmlFor="password">Password</CustomFormLabel>
            <CustomTextField
              id="password"
              variant="outlined"
              fullWidth
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
            />
          </Stack>
          <Button
            color="primary"
            variant="contained"
            size="large"
            fullWidth
            type="submit"
          >
            Register
          </Button>
        </form>
      </Box>
      {subtitle}
    </>
  );
};

export default AuthRegister;
