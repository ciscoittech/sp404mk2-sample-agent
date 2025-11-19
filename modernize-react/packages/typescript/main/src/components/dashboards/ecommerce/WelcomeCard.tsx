// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Box, Avatar, Typography, Card, CardContent, Grid, Divider, Stack } from '@mui/material';
import { IconArrowUpRight } from '@tabler/icons-react';

import welcomeImg from 'src/assets/images/backgrounds/welcome-bg2.png';
import userImg from 'src/assets/images/profile/user-1.jpg';

const WelcomeCard = () => {
  return (
    (<Card elevation={0} sx={{ backgroundColor: (theme) => theme.palette.primary.light, py: 0 }}>
      <CardContent sx={{ py: 4, px: 2 }}>
        <Grid container justifyContent="space-between">
          <Grid
            display="flex"
            alignItems="center"
            size={{
              sm: 6
            }}>
            <Box>
              <Box
                gap="16px" mb={5}
                sx={{
                  display: {
                    xs: 'block',
                    sm: 'flex',
                  },
                  alignItems: 'center',
                }}
              >
                <Avatar src={userImg} alt="img" sx={{ width: 40, height: 40 }} />
                <Typography variant="h5" whiteSpace="nowrap">
                  Welcome back Mathew Anderson!
                </Typography>
              </Box>

              <Stack spacing={2} direction="row" divider={<Divider orientation="vertical" flexItem />}>
                <Box>
                  <Typography variant="h2" whiteSpace="nowrap">$2,340 <span><IconArrowUpRight width={18} color="#39B69A" /></span></Typography>
                  <Typography variant="subtitle1" whiteSpace="nowrap">Today’s Sales</Typography>
                </Box>
                <Box>
                  <Typography variant="h2" whiteSpace="nowrap">35%<span><IconArrowUpRight width={18} color="#39B69A" /></span></Typography>
                  <Typography variant="subtitle1" whiteSpace="nowrap">Performance</Typography>
                </Box>
              </Stack>
            </Box>
          </Grid>
          <Grid
            size={{
              sm: 6
            }}>
            <Box mb="-88px" textAlign="right">
              <img src={welcomeImg} alt={welcomeImg} width={'300px'} />
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>)
  );
};

export default WelcomeCard;
