import { Grid, Typography } from '@mui/material';

const keys = [
  {
    text: 'Founded',
    title: '2019',
    subtext: 'When we founded Modernize',
  },
  {
    text: 'Growth',
    title: '1,400%',
    subtext: 'Revenue growth in 2024',
  },
  {
    text: 'Customers',
    title: '300k+',
    isMargin: true,
    subtext: 'Customers on Modernize',
  },
  {
    text: 'Dashboards',
    title: '25k+',
    isMargin: true,
    subtext: 'Dashboards built using Modernize',
  },
];

const Key = () => {
  return (
    (<Grid container spacing={2}>
      {keys.map((key, i) => (
        <Grid
          key={i}
          sx={{
            marginTop: {
              lg: key.isMargin ? '32px' : 0,
            },
          }}
          size={{
            xs: 6,
            sm: 6
          }}>
          <Typography color="primary.main" textTransform="uppercase" fontSize="13px">
            {key.text}
          </Typography>
          <Typography
            variant="h4"
            sx={{
              fontSize: {
                xs: '34px',
                sm: '48px',
              },
            }}
            my={1}
            lineHeight={1}
            fontWeight={700}
          >
            {key.title}
          </Typography>
          <Typography variant="body1">{key.subtext}</Typography>
        </Grid>
      ))}
    </Grid>)
  );
};

export default Key;
