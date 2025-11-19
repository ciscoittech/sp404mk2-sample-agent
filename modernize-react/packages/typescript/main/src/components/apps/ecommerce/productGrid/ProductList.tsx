// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useEffect, useContext } from 'react';

import {
  Box,
  Grid,
  Stack,
  CardContent,
  useMediaQuery,
  Typography,
  Rating,
  Fab,
  Tooltip,
  Button,
  Theme,
  Skeleton,
} from '@mui/material';
import { Link } from 'react-router';

import { ProductContext } from "src/context/EcommerceContext";
import ProductSearch from './ProductSearch';
import { IconBasket, IconMenu2 } from '@tabler/icons-react';
import AlertCart from '../productCart/AlertCart';
import emptyCart from 'src/assets/images/products/empty-shopping-cart.svg';
import BlankCard from '../../../shared/BlankCard';


interface Props {
  onClick: (event: React.SyntheticEvent | Event) => void;
}

const ProductList = ({ onClick }: Props) => {


  const { filteredAndSortedProducts, addToCart, filterReset } =
    useContext(ProductContext);

  const lgUp = useMediaQuery((theme: Theme) => theme.breakpoints.up('lg'));




  // for alert when added something to cart
  const [cartalert, setCartalert] = React.useState(false);

  const handleClick = () => {

    setCartalert(true);
  };

  const handleClose = (reason: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setCartalert(false);
  };

  // skeleton
  const [isLoading, setLoading] = React.useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    (<Box>
      {/* ------------------------------------------- */}
      {/* Header Detail page */}
      {/* ------------------------------------------- */}
      <Stack direction="row" justifyContent="space-between" pb={3}>
        {lgUp ? (
          <Typography variant="h5">Products</Typography>
        ) : (
          <Fab onClick={onClick} color="primary" size="small">
            <IconMenu2 width="16" />
          </Fab>
        )}
        <Box>
          <ProductSearch />
        </Box>
      </Stack>
      {/* ------------------------------------------- */}
      {/* Page Listing product */}
      {/* ------------------------------------------- */}
      <Grid container spacing={3}>
        {filteredAndSortedProducts.length > 0 ? (
          <>
            {filteredAndSortedProducts.map((product) => (
              <Grid
                display="flex"
                alignItems="stretch"
                key={product.id}
                size={{
                  xs: 12,
                  lg: 4,
                  md: 4,
                  sm: 6
                }}>
                {/* ------------------------------------------- */}
                {/* Product Card */}
                {/* ------------------------------------------- */}
                {isLoading ? (
                  <>
                    <Skeleton
                      variant="rectangular"
                      width={270}
                      height={300}
                      sx={{ borderRadius: (theme) => theme.shape.borderRadius / 5 }}
                    ></Skeleton>
                  </>
                ) : (
                  <BlankCard className="hoverCard">
                    <Typography component={Link} to={`/apps/ecommerce/detail/${product.id}`}>
                      <img src={product.photo} alt="img" width="100%" />
                    </Typography>
                    <Tooltip title="Add To Cart">
                      <Fab
                        size="small"
                        color="primary"
                        onClick={() => {
                          addToCart(product.id);
                          handleClick();
                        }}
                        sx={{ bottom: '75px', right: '15px', position: 'absolute' }}
                      >
                        <IconBasket size="16" />
                      </Fab>
                    </Tooltip>
                    <CardContent sx={{ p: 3, pt: 2 }}>
                      <Typography variant="h6">{product.title}</Typography>
                      <Stack
                        direction="row"
                        alignItems="center"
                        justifyContent="space-between"
                        mt={1}
                      >
                        <Stack direction="row" alignItems="center">
                          <Typography variant="h6">${product.price}</Typography>
                          <Typography
                            color="textSecondary"
                            ml={1}
                            sx={{ textDecoration: 'line-through' }}
                          >
                            ${product.salesPrice}
                          </Typography>
                        </Stack>
                        <Rating name="read-only" size="small" value={product.rating} readOnly />
                      </Stack>
                    </CardContent>
                  </BlankCard>
                )}
                <AlertCart handleClose={handleClose} openCartAlert={cartalert} />
                {/* ------------------------------------------- */}
                {/* Product Card */}
                {/* ------------------------------------------- */}
              </Grid>
            ))}
          </>
        ) : (
          <>
            <Grid
              size={{
                xs: 12,
                lg: 12,
                md: 12,
                sm: 12
              }}>
              <Box textAlign="center" mt={6}>
                <img src={emptyCart} alt="cart" width="200px" />
                <Typography variant="h2">There is no Product</Typography>
                <Typography variant="h6" mb={3}>
                  The Product you are searching is no longer available.
                </Typography>
                <Button variant="contained" onClick={filterReset}>
                  Try Again
                </Button>
              </Box>
            </Grid>
          </>
        )}
      </Grid>
    </Box>)
  );
};

export default ProductList;
