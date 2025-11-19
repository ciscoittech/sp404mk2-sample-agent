import React from 'react';
import { Box, Stack, Typography, Link, AvatarGroup, Container, Avatar } from '@mui/material';

import user1 from 'src/assets/images/profile/user-1.jpg';
import user2 from 'src/assets/images/profile/user-2.jpg';

const Contact = () => {
  return (
    <Box
      bgcolor="primary.main"
      borderRadius={0}
      textAlign="center"
      py="14px"
      mt={5}
      position="relative"
    >
      <Container maxWidth="lg">
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing="16px"
          justifyContent="center"
          alignItems="center"
        >
          <AvatarGroup>
            <Avatar alt="Remy Sharp" src={user1} sx={{ width: 44, height: 44 }} />
            <Avatar alt="Travis Howard" src={user2} sx={{ width: 44, height: 44 }} />
          </AvatarGroup>
          <Typography variant="body1" color="white" fontSize="16px">
            Save valuable time and effort spent searching for a solution.
          </Typography>
          <Link
            href="/"
            underline="always"
            sx={{
              textDecorationColor: 'white',
            }}
          >
            <Typography component="span" fontWeight={600} color="white" fontSize="16px">
              Contact us now
            </Typography>
          </Link>
        </Stack>
      </Container>
    </Box>
  );
};

export default Contact;
