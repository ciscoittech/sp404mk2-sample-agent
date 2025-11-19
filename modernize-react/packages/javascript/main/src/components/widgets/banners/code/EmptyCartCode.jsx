import CodeDialog from '../../../shared/CodeDialog';
import React from 'react';
const EmptyCartCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { CardContent, Typography, Button, Box,  Card } from '@mui/material';

const Banner5 = () => {
  return (
    <Card>
      <CardContent sx={{ p: '30px' }}>
        <Box textAlign="center">
          <img src={"/images/products/empty-shopping-cart.svg"} width={200} height={200} alt="star" style={{ width: '200px' }} />

          <Typography variant="h5" mt={3}>Oop, Your cart is empty!</Typography>
          <Typography variant="subtitle1" color="textSecondary" mt={1} mb={2}>
            Get back to shopping and get<br /> rewards from it.
          </Typography>

          <Button color="primary" variant="contained" size="large">
            Go for shopping!
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default Banner5;
`}
      </CodeDialog>
    </>
  );
};

export default EmptyCartCode;
