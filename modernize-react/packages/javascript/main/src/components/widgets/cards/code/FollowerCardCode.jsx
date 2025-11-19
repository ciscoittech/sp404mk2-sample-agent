import CodeDialog from '../../../shared/CodeDialog';
import React from 'react';
const FollowerCardCode = () => {
  return (
    <>
      <CodeDialog>
        {`
import React from 'react';
import { CardContent, Typography, Button, Avatar, Box, Card, stack } from '@mui/material';
import { Grid } from '@mui/material';
import { IconMapPin } from '@tabler/icons';

const followerCard = [
  {
    title: 'Andrew Grant',
    location: 'El Salvador',
    avatar: "/images/profile/user-1.jpg",
  },
  {
    title: 'Leo Pratt',
    location: 'Bulgaria',
    avatar: "/images/profile/user-2.jpg",
  },
  {
    title: 'Charles Nunez',
    location: 'Nepal',
    avatar: "/images/profile/user-3.jpg",
  },
];

const FollowerCard = () => {
  return (
    <Grid container spacing={3}>
      {followerCard.map((card, index) => (
        <Grid size={{xs: 12, sm: 4}}  key={index}>
          <Card>
            <CardContent>
              <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
                <Stack direction="row" spacing={2}>
                  <Avatar src={card.avatar} alt={card.avatar} />
                  <Box>
                    <Typography variant="h6">{card.title}</Typography>
                    <Typography
                      variant="subtitle1"
                      color="textSecondary"
                      display="flex"
                      alignItems="center"
                      gap="3px"
                    >
                      <IconMapPin width={18} /> {card.location}
                    </Typography>
                  </Box>
                </Stack>
                <Button variant="contained" color="primary">
                  Follow
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default FollowerCard;
`}
      </CodeDialog>
    </>
  );
};

export default FollowerCardCode;
