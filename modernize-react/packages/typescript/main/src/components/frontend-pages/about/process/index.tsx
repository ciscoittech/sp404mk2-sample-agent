import { Box, Stack, Typography, Grid, Container, Divider } from '@mui/material';

import Icon1 from 'src/assets/images/svgs/icon-briefcase.svg';
import FeatureApp from 'src/assets/images/frontend-pages/homepage/feature-apps.png';
import IconBubble from 'src/assets/images/svgs/icon-speech-bubble.svg';
import IconFav from 'src/assets/images/svgs/icon-favorites.svg';

const Process = () => {
  return (
    (<Box pt={10}>
      <Container maxWidth="lg">
        <Grid container spacing={3} justifyContent="center">
          <Grid
            textAlign="center"
            size={{
              xs: 12,
              lg: 7
            }}>
            <Typography
              variant="h4"
              sx={{
                fontSize: {
                  lg: '40px',
                  xs: '35px',
                },
              }}
              fontWeight="700"
              mt={5}
            >
              The hassle-free setup process
            </Typography>
          </Grid>
        </Grid>

        <Grid container spacing={3} mt={3}>
          <Grid
            size={{
              xs: 12,
              sm: 6,
              lg: 3
            }}>
            <Box mb={3} bgcolor="warning.light" borderRadius="24px">
              <Box px="20px" py="32px">
                <Stack direction="column" spacing={2} mt={2} textAlign="center">
                  <Box textAlign="center">
                    <img src={Icon1} alt="icon1" width={40} height={40} />
                  </Box>
                  <Typography variant="h6" fontWeight={700}>
                    Light & Dark Color Schemes
                  </Typography>
                  <Typography variant="body1">
                    Choose your preferred visual style effortlessly.
                  </Typography>
                </Stack>
              </Box>
            </Box>
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6,
              lg: 3
            }}>
            <Box
              textAlign="center"
              mb={3}
              bgcolor="secondary.light"
              borderRadius="24px"
              overflow="hidden"
            >
              <Box px="20px" pt="26px" pb="20px">
                <Stack direction="column" spacing={2} textAlign="center">
                  <Typography variant="h6" fontWeight={700} px={1} lineHeight={1.4}>
                    12+ Ready to Use Application Designs
                  </Typography>
                  <Typography variant="body1">
                    {' '}
                    Instantly deployable designs for your applications.
                  </Typography>
                </Stack>
              </Box>
              <Box height="70px">
                <img src={FeatureApp} alt="icon1" width={250} height={70} />
              </Box>
            </Box>
          </Grid>

          <Grid
            size={{
              xs: 12,
              sm: 6,
              lg: 3
            }}>
            <Box textAlign="center" mb={3} bgcolor="success.light" borderRadius="24px">
              <Box px="20px" py="32px">
                <Stack direction="column" spacing={2} mt={2} textAlign="center">
                  <Box textAlign="center">
                    <img src={IconBubble} alt="icon1" width={40} height={40} />
                  </Box>
                  <Typography variant="h6" fontWeight={700}>
                    Code Improvements
                  </Typography>
                  <Typography variant="body1">
                    {' '}
                    Benefit from continuous improvements and optimizations.
                  </Typography>
                </Stack>
              </Box>
            </Box>
          </Grid>
          <Grid
            size={{
              xs: 12,
              sm: 6,
              lg: 3
            }}>
            <Box textAlign="center" mb={3} bgcolor="error.light" borderRadius="24px">
              <Box px="20px" py="32px">
                <Stack direction="column" spacing={2} mt={2} textAlign="center">
                  <Box textAlign="center">
                    <img src={IconFav} alt="icon1" width={40} height={40} />
                  </Box>
                  <Typography variant="h6" fontWeight={700}>
                    50+ UI Components
                  </Typography>
                  <Typography variant="body1">
                    {' '}
                    A rich collection for seamless user experiences.
                  </Typography>
                </Stack>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Container>
      <Divider
        sx={{
          mt: '65px',
        }}
      />
    </Box>)
  );
};

export default Process;
