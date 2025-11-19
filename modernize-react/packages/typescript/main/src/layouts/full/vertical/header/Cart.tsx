// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useState, useContext } from 'react';
import { sum } from 'lodash';
import { IconShoppingCart, IconX } from '@tabler/icons-react';
import { Box, Typography, Badge, Drawer, IconButton, Button, Stack } from '@mui/material';
import { Link } from 'react-router';
import CartItems from './CartItem';
import { ProductContext } from 'src/context/EcommerceContext';


const Cart = () => {


  const {
    cartItems,
  } = useContext(ProductContext);

  const bcount = cartItems.length > 0 ? cartItems.length : '0';

  const total = sum(cartItems.map((product: any) => product.price * product.qty));


  const [showDrawer, setShowDrawer] = useState(false);
  const handleDrawerClose = () => {
    setShowDrawer(false);
  };

  const cartContent = (
    <Box>
      {/* ------------------------------------------- */}
      {/* Cart Content */}
      {/* ------------------------------------------- */}
      <Box>
        <CartItems />
      </Box>
    </Box>
  );

  return (
    (<Box>
      <IconButton
        size="large"
        color="inherit"
        onClick={() => setShowDrawer(true)}
        sx={{
          color: 'text.secondary',
          ...(showDrawer && {
            color: 'primary.main',
          }),
        }}
      >
        <Badge color="error" badgeContent={bcount}>
          <IconShoppingCart size="21" stroke="1.5" />
        </Badge>
      </IconButton>
      {/* ------------------------------------------- */}
      {/* Cart Sidebar */}
      {/* ------------------------------------------- */}
      <Drawer
        anchor="right"
        open={showDrawer}
        onClose={() => setShowDrawer(false)}
        slotProps={{
          paper: { sx: { maxWidth: '500px' } }
        }}
      >
        <Box display="flex" alignItems="center" p={3} pb={0} justifyContent="space-between">
          <Typography variant="h5" fontWeight={600}>
            Shopping Cart
          </Typography>
          <Box>
            <IconButton
              color="inherit"
              sx={{
                color: (theme) => theme.palette.grey.A200,
              }}
              onClick={handleDrawerClose}
            >
              <IconX size="1rem" />
            </IconButton>
          </Box>
        </Box>

        {/* component */}
        {cartContent}
        {/* ------------------------------------------- */}
        {/* Checkout  */}
        {/* ------------------------------------------- */}
        <Box px={3} mt={2}>
          {cartItems.length > 0 ? (
            <>
              <Stack direction="row" justifyContent="space-between" mb={3}>
                <Typography variant="subtitle2" fontWeight={400}>
                  Total
                </Typography>
                <Typography variant="subtitle2" fontWeight={600}>
                  ${total}
                </Typography>
              </Stack>
              <Button
                fullWidth
                component={Link}
                to="/apps/ecommerce/eco-checkout"
                variant="contained"
                color="primary"
              >
                Checkout
              </Button>
            </>
          ) : (
            ''
          )}
        </Box>
      </Drawer>
    </Box>)
  );
};

export default Cart;
