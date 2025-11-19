import { Box, Container, Grid } from '@mui/material';
import ContentArea from './ContentArea';
import Key from './Key';

const KeyMetric = () => {
  return (
    (<Box
      sx={{
        paddingTop: {
          xs: '40px',
          lg: '90px',
        },
        paddingBottom: {
          xs: '40px',
          lg: '90px',
        },
        boxShadow: (theme) => theme.shadows[10],
      }}
    >
      <Container maxWidth="lg">
        <Grid container spacing={3} justifyContent="space-between">
          <Grid
            size={{
              xs: 12,
              lg: 5
            }}>
            <ContentArea />
          </Grid>
          <Grid
            size={{
              xs: 12,
              lg: 5
            }}>
            <Key />
          </Grid>
        </Grid>
      </Container>
    </Box>)
  );
};

export default KeyMetric;
