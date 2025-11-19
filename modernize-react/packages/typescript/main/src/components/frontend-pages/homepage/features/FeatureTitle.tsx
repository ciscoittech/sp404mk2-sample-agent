import { Box, Grid, Typography } from '@mui/material';

const FeatureTitle = () => {
  return (
    (<Grid container spacing={3} justifyContent="center">
      <Grid
        textAlign="center"
        size={{
          xs: 12,
          lg: 6
        }}>
        <Typography variant="body1">
          Introducing Modernize's Light & Dark Skins,{' '}
          <Box fontWeight={500} component="span">
            Exceptional Dashboards
          </Box>
          , and <br />
          Dynamic Pages - Stay Updated on What's New!
        </Typography>
      </Grid>
    </Grid>)
  );
};

export default FeatureTitle;
