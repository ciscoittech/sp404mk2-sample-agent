import { Box, Typography, Container, Grid } from '@mui/material';

const Banner = () => {
  return (<>
    <Box
      bgcolor="primary.light"
      sx={{
        paddingTop: {
          xs: '40px',
          lg: '100px',
        },
        paddingBottom: {
          xs: '40px',
          lg: '200px',
        },
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={3} justifyContent="center">
          <Grid
            alignItems="center"
            textAlign="center"
            size={{
              xs: 12,
              lg: 8
            }}>
            <Typography color="primary.main" textTransform="uppercase" fontSize="13px">
              Contact us
            </Typography>
            <Typography
              variant="h1"
              mb={3}
              lineHeight={1.4}
              fontWeight={700}
              sx={{
                fontSize: {
                  xs: '34px',
                  sm: '48px',
                  lg: '56px',
                },
              }}
            >
              We'd love to hear from you
            </Typography>
          </Grid>
        </Grid>
      </Container>
    </Box>
    <Box
      sx={{
        mt: {
          lg: '-150px',
        },
      }}
    >
      <Container maxWidth="lg">
        <iframe
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3388599.4592369436!2d6.920799949782969!3d33.96223431657389!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x125595448316a4e1%3A0x3a84333aaa019bef!2sTunisia!5e0!3m2!1sen!2sin!4v1726146847742!5m2!1sen!2sin"
          width="100%"
          height="440"
          style={{ border: 0 }}
          allowFullScreen
          loading="lazy"
        ></iframe>
      </Container>
    </Box>
  </>);
};

export default Banner;
