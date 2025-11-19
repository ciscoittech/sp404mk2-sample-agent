import CodeDialog from '../../../shared/CodeDialog';
import React from 'react';
const NotificationCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { CardContent, Typography, Button, Card, Box } from '@mui/material';

const Banner2 = () => {
  return (
    <Card>
      <CardContent sx={{ p: '30px' }}>
        <Typography variant="subtitle1" textAlign="center" mb={2} textTransform="uppercase" color="textSecondary">
          Level Up
        </Typography>
        <Box textAlign="center">
          <Image src={"/images/backgrounds/gold.png"} width={150} height={150} alt="star" style={{ width: '150px'}} />

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
