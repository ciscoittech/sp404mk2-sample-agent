import { Box, Grid, Typography, Container, Stack, Button } from '@mui/material';
import useMediaQuery from '@mui/material/useMediaQuery';

import DesignCol from 'src/assets/images/frontend-pages/homepage/design-collection.png';

const C2a = () => {
  const lgUp = useMediaQuery((theme: any) => theme.breakpoints.up('lg'));
  const smUp = useMediaQuery((theme: any) => theme.breakpoints.only('sm'));

  return (<>
    <Container
      sx={{
        maxWidth: '1400px !important',
        py: {
          xs: '20px',
          lg: '30px',
        },
      }}
    >
      <Box
        bgcolor="primary.light"
        borderRadius="24px"
        overflow="hidden"
        position="relative"
        sx={{
          py: {
            xs: '40px',
            lg: '70px',
          },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3} alignItems="center">
            <Grid
              size={{
                xs: 12,
                lg: 6,
                sm: 8
              }}>
              <Typography
                variant="h4"
                mb={3}
                fontWeight={700}
                fontSize="40px"
                lineHeight="1.4"
                sx={{
                  fontSize: {
                    lg: '40px',
                    xs: '30px',
                  },
                }}
              >
                Develop with feature-rich React Dashboard
              </Typography>
              <Stack spacing={{ xs: 1, sm: 2 }} direction="row" flexWrap="wrap" mb={3}>
                <Button variant="contained" size="large" href="/auth/login">
                  Member Login
                </Button>
                <Button variant="outlined" size="large" href="/auth/register">
                  Register as Member
                </Button>
              </Stack>
              <Typography fontSize="14px">
                <Box fontWeight={600} component="span">
                  One-time purchase -
                </Box>{' '}
                no recurring fees.
              </Typography>
            </Grid>
          </Grid>
        </Container>

        {lgUp ? (
          <img
            src={DesignCol}
            alt="design"
            width={900}
            height={365}
            style={{
              position: 'absolute',
              right: 0,
              top: 0,
              width: 'auto',
              height: '100%',
            }}
          />
        ) : null}

        {smUp ? (
          <img
            src={DesignCol}
            alt="design"
            width={900}
            height={365}
            style={{
              position: 'absolute',
              right: '-200px',
              top: 0,
              width: 'auto',
              height: '100%',
            }}
          />
        ) : null}
      </Box>
    </Container>
  </>);
};

export default C2a;
