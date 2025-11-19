import CodeDialog from '../../../shared/CodeDialog';
import React from 'react';
const EcommerceCardCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React, { useEffect } from 'react';
import { Link } from 'react-router';
import { CardContent, Typography, Rating, Tooltip, Fab, Card, stack } from '@mui/material';
import { Grid } from '@mui/material';
import { IconBasket } from '@tabler/icons';
import Image from 'next/image';

const ecoCard = [
  {
    title: 'Boat Headphone',
    subheader: 'September 14, 2025',
    photo: "/images/products/s4.jpg",
    salesPrice: 375,
    price: 285,
    rating: 4,
  },
  {
    title: 'MacBook Air Pro',
    subheader: 'September 14, 2025',
    photo: "/images/products/s5.jpg",
    salesPrice: 650,
    price: 900,
    rating: 5,
  },
  {
    title: 'Red Valvet Dress',
    subheader: 'September 14, 2025',
    photo: "/images/products/s7.jpg",
    salesPrice: 150,
    price: 200,
    rating: 3,
  },
  {
    title: 'Cute Soft Teddybear',
    subheader: 'September 14, 2025',
    photo: "/images/products/s11.jpg",
    salesPrice: 285,
    price: 345,
    rating: 2,
  },
];

const EcommerceCard = () => {
  return (
    <Grid container spacing={3}>
      {ecoCard.map((product, index) => (
        <Grid size={{xs: 12, sm: 4, lg: 3}} key={index}>
          <Card>
            <Typography component={Link} to="/">
              <Image src={product.photo} alt="img" width={250} height={268} style={{width: '100%'}} />
            </Typography>
            <Tooltip title="Add To Cart">
              <Fab
                size="small"
                color="primary"
                sx={{ bottom: '75px', right: '15px', position: 'absolute' }}
              >
                <IconBasket size="16" />
              </Fab>
            </Tooltip>
            <CardContent sx={{ p: 3, pt: 2 }}>
              <Typography variant="h6">{product.title}</Typography>
              <Stack direction="row" alignItems="center" justifyContent="space-between" mt={1}>
                <Stack direction="row" alignItems="center">
                  <Typography variant="h6">{product.price}</Typography>
                  <Typography color="textSecondary" ml={1} sx={{ textDecoration: 'line-through' }}>
                    {product.salesPrice}
                  </Typography>
                </Stack>
                <Rating name="read-only" size="small" value={product.rating} readOnly />
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default EcommerceCard;

`}
      </CodeDialog>
    </>
  );
};

export default EcommerceCardCode;
