import React from 'react';
import { Box, Stack, Typography, AvatarGroup, Avatar, Container, Button } from '@mui/material';
import { Grid } from '@mui/material';
import useMediaQuery from '@mui/material/useMediaQuery';
import Tooltip from '@mui/material/Tooltip';

import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';

// icons
import icon1 from 'src/assets/images/frontend-pages/icons/icon-react.svg';
import icon2 from 'src/assets/images/frontend-pages/icons/icon-mui.svg';
import icon3 from 'src/assets/images/frontend-pages/icons/icon-next.svg';
import icon4 from 'src/assets/images/frontend-pages/icons/icon-ts.svg';
import icon5 from 'src/assets/images/frontend-pages/icons/logos_swr.svg';
import icon6 from 'src/assets/images/frontend-pages/icons/icon-tabler.svg';

import BannerTopLeft from 'src/assets/images/frontend-pages/homepage/banner-top-left.svg';
import BannerBottomPart from 'src/assets/images/frontend-pages/homepage/bottom-part.svg';
import BannerTopRight from 'src/assets/images/frontend-pages/homepage/banner-top-right.svg';

import user1 from 'src/assets/images/profile/user-1.jpg';
import user2 from 'src/assets/images/profile/user-2.jpg';
import user3 from 'src/assets/images/profile/user-3.jpg';

import iconPlay from 'src/assets/images/frontend-pages/homepage/icon-play.svg';

const Frameworks = [
  {
    name: 'React',
    icon: icon1,
  },
  {
    name: 'Material Ui',
    icon: icon2,
  },
  {
    name: 'Typescript',
    icon: icon4,
  },
  {
    name: 'Swr',
    icon: icon5,
  },
  {
    name: 'Tabler Icon',
    icon: icon6,
  },
];
const Banner = () => {
  //   sidebar
  const lgUp = useMediaQuery((theme) => theme.breakpoints.up('lg'));

  const [open, setOpen] = React.useState(false);

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  return (
    (<Box bgcolor="primary.light" pt={7}>
      <Container
        sx={{
          maxWidth: '1400px !important',
          position: 'relative',
        }}
      >
        <Grid container spacing={3} justifyContent="center" mb={4}>
          {lgUp ? (
            <Grid size={{ xs: 12, lg: 2 }} alignItems="end" display="flex">
              <img
                src={BannerTopLeft}
                className="animted-img-2"
                alt="banner"
                width={360}
                height={200}
                style={{
                  borderRadius: '16px',
                  position: 'absolute',
                  left: '24px',
                  boxShadow: (theme) => theme.shadows[10],
                  height: 'auto',
                  width: 'auto',
                }}
              />
            </Grid>
          ) : null}

          <Grid size={{ xs: 12, lg: 7 }} textAlign="center">
            <Typography
              variant="h1"
              fontWeight={700}
              lineHeight="1.2"
              sx={{
                fontSize: {
                  xs: '40px',
                  sm: '56px',
                },
              }}
            >
              Most powerful &{' '}
              <Typography
                variant="h1"
                sx={{
                  fontSize: {
                    xs: '40px',
                    sm: '56px',
                  },
                }}
                fontWeight={700}
                component="span"
                color="primary.main"
              >
                developer friendly
              </Typography>{' '}
              dashboard
            </Typography>
            <Stack
              my={3}
              direction={{ xs: 'column', sm: 'row' }}
              spacing="20px"
              alignItems="center"
              justifyContent="center"
            >
              <AvatarGroup>
                <Avatar alt="Remy Sharp" src={user1} sx={{ width: 40, height: 40 }} />
                <Avatar alt="Travis Howard" src={user2} sx={{ width: 40, height: 40 }} />
                <Avatar alt="Cindy Baker" src={user3} sx={{ width: 40, height: 40 }} />
              </AvatarGroup>
              <Typography variant="h6" fontWeight={500}>
                52,589+ developers & agencies using our templates
              </Typography>
            </Stack>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              alignItems="center"
              spacing={3}
              mb={4}
              justifyContent="center"
            >
              <Button color="primary" size="large" variant="contained" href="/auth/login">
                Log In
              </Button>
              <Button
                variant="text"
                color="inherit"
                onClick={handleClickOpen}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 2,
                  color: 'text.primary',
                  fontWeight: 500,
                  fontSize: '15px',
                  '&:hover': {
                    color: 'primary.main',
                  },
                }}
              >
                <img src={iconPlay} alt="icon" width={40} height={40} /> See how it works
              </Button>

              <Dialog
                maxWidth="lg"
                open={open}
                onClose={handleClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
              >
                <DialogContent>
                  <iframe
                    width="800"
                    height="500"
                    src="https://www.youtube.com/embed/P94DBd1hJkw?si=WLnH9g-KAdDJkUZN"
                    title="YouTube video player"
                    frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    referrerpolicy="strict-origin-when-cross-origin"
                    allowFullScreen
                  ></iframe>
                </DialogContent>
                <DialogActions>
                  <Button onClick={handleClose} autoFocus>
                    Close
                  </Button>
                </DialogActions>
              </Dialog>
            </Stack>
            <Stack
              direction="row"
              flexWrap="wrap"
              useflexgap="true"
              alignItems="center"
              spacing={3}
              mb={8}
              justifyContent="center"
            >
              {Frameworks.map((fw, i) => (
                <Tooltip title={fw.name} key={i}>
                  <Box
                    width="54px"
                    height="54px"
                    display="flex"
                    sx={{
                      boxShadow: (theme) =>
                        theme.palette.mode === 'dark' ? null : (theme) => theme.shadows[10],
                      backgroundColor: (theme) =>
                        theme.palette.mode === 'dark' ? '#1f2c4f' : 'white',
                    }}
                    alignItems="center"
                    justifyContent="center"
                    borderRadius="16px"
                  >
                    <img src={fw.icon} alt={fw.icon} width={26} height={26} />
                  </Box>
                </Tooltip>
              ))}
            </Stack>
          </Grid>
          {lgUp ? (
            <Grid
              size={{ xs: 12, lg: 2 }}
              alignItems="end"
              display="flex"
            >
              <img
                src={BannerTopRight}
                className="animted-img-2"
                alt="banner"
                width={350}
                height={220}
                style={{
                  borderRadius: '16px',
                  position: 'absolute',
                  right: '24px',
                  boxShadow: (theme) => theme.shadows[10],
                  height: 'auto',
                  width: 'auto',
                }}
              />
            </Grid>
          ) : null}
        </Grid>

        {lgUp ? (
          <img
            src={BannerBottomPart}
            alt="banner"
            width={500}
            height={300}
            style={{
              width: '100%',
              marginBottom: '-11px',
            }}
          />
        ) : null}
      </Container>
    </Box>)
  );
};

export default Banner;
