import CodeDialog from 'src/components/shared/CodeDialog';
const NotificationCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { CardContent, Typography, Button, Card } from '@mui/material';
import { Box } from '@mui/system';

const Banner2 = () => {
  return (
    <Card>
      <CardContent sx={{ p: '30px' }}>
        <Typography variant="subtitle1" textAlign="center" mb={2} textTransform="uppercase" color="textSecondary">
          Level Up
        </Typography>
        <Box textAlign="center">
          <img src={"/images/backgrounds/gold.png"} alt="star" width={150} />

          <Typography variant="h5">You reach all Notifications</Typography>
          <Typography variant="subtitle1" color="textSecondary" mt={1} mb={2}>Congratulations,<br/> Tap to continue next task.</Typography>

          <Button color="primary" variant="contained" size="large">
            Yes, Got it!
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default Banner2;
`}
      </CodeDialog>
    </>
  );
};

export default NotificationCode;
