import React from 'react';
import { Grid, Typography, Box, Breadcrumbs, Link } from '@mui/material';
import { NavLink } from 'react-router';

import breadcrumbImg from 'src/assets/images/breadcrumb/ChatBc.png';
import { IconCircle } from '@tabler/icons-react';

const Breadcrumb = ({ subtitle, items, title, children }) => (
  <Grid
    container
    sx={{
      backgroundColor: 'primary.light',
      borderRadius: (theme) => theme.shape.borderRadius / 4,
      p: '30px 25px 20px',
      marginBottom: '30px',
      position: 'relative',
      overflow: 'hidden',
    }}
  >
    <Grid
      mb={1}
      size={{
        xs: 12,
        sm: 6,
        lg: 8
      }}>
      <Typography variant="h4">{title}</Typography>
      <Typography color="textSecondary" variant="h6" fontWeight={400} mt={0.8} mb={0}>
        {subtitle}
      </Typography>
      <Breadcrumbs
        separator={
          <IconCircle
            size="5"
            fill="textSecondary"
            fillOpacity={'0.6'}
            style={{ margin: '0 5px' }}
          />
        }
        sx={{ alignItems: 'center', mt: items ? '10px' : '' }}
        aria-label="breadcrumb"
      >
        {items
          ? items.map((item) => (
            <div key={item.title}>
              {item.to ? (
                <Link underline="none" color="inherit" component={NavLink} to={item.to}>
                  {item.title}
                </Link>
              ) : (
                <Typography color="textPrimary">{item.title}</Typography>
              )}
            </div>
          ))
          : ''}
      </Breadcrumbs>
    </Grid>
    <Grid
      display="flex"
      alignItems="flex-end"
      size={{
        xs: 12,
        sm: 6,
        lg: 4
      }}>
      <Box
        sx={{
          display: { xs: 'none', md: 'block', lg: 'flex' },
          alignItems: 'center',
          justifyContent: 'flex-end',
          width: '100%',
        }}
      >
        {children ? (
          <Box sx={{ top: '0px', position: 'absolute' }}>{children}</Box>
        ) : (
          <>
            <Box sx={{ top: '0px', position: 'absolute' }}>
              <img src={breadcrumbImg} alt={breadcrumbImg} width={'165px'} />
            </Box>
          </>
        )}
      </Box>
    </Grid>
  </Grid>
);

export default Breadcrumb;
