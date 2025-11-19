// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useEffect } from 'react';
import { CardContent, Typography, Grid, IconButton, Divider, Avatar, Box, Stack, Skeleton } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  IconBrandFacebook,
  IconBrandGithub,
  IconBrandInstagram,
  IconBrandTwitter,
} from '@tabler/icons-react';
import img1 from 'src/assets/images/profile/user-1.jpg';
import img2 from 'src/assets/images/profile/user-2.jpg';
import img3 from 'src/assets/images/profile/user-3.jpg';
import BlankCard from '../../shared/BlankCard';
import ParentCard from '../../shared/ParentCard';

import ProfileCardCode from './code/ProfileCardCode';

interface SocialIcon {
  name: string;
  icon: any;
}

interface ProfileCard {
  name: string;
  role: string;
  avatar: string;
}

const SocialIcons: SocialIcon[] = [
  {
    name: 'Facebook',
    icon: <IconBrandFacebook size="18" color="#1877F2" />,
  },
  {
    name: 'Instagram',
    icon: <IconBrandInstagram size="18" color="#D7336D" />,
  },
  {
    name: 'Github',
    icon: <IconBrandGithub size="18" color="#006097" />,
  },
  {
    name: 'Twitter',
    icon: <IconBrandTwitter size="18" color="#1C9CEA" />,
  },
];

const profileCard: ProfileCard[] = [
  {
    name: 'Andrew Grant',
    role: 'Technology Director',
    avatar: img1,
  },
  {
    name: 'Leo Pratt',
    role: 'Telecom Analyst',
    avatar: img2,
  },
  {
    name: 'Charles Nunez',
    role: 'Environmental Specialist',
    avatar: img3,
  },
];

const ProfileCard = () => {

  const theme = useTheme();
  const [isLoading, setLoading] = React.useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 700);

    return () => clearTimeout(timer);
  }, []);


  return (
    (<ParentCard title='Profile Card' codeModel={<ProfileCardCode />}>
      <Grid container spacing={3}>
        {profileCard.map((card, index) => (
          <Grid
            key={index}
            size={{
              xs: 12,
              sm: 4
            }}>
            <BlankCard>
              <CardContent>
                <Stack direction={'column'} gap={2} alignItems="center">
                  {isLoading ? (
                    <Skeleton variant="rectangular" animation="wave" width="100%" height={160}></Skeleton>
                  ) : (
                    <Avatar alt="Remy Sharp" src={card.avatar} sx={{ width: '80px', height: '80px' }} />
                  )}
                  <Box textAlign={'center'}>
                    <Typography variant="h5">{card.name}</Typography>
                    <Typography variant="caption">{card.role}</Typography>
                  </Box>
                </Stack>
              </CardContent>
              <Divider />
              <Box
                p={2}
                py={1}
                textAlign={'center'}
                sx={{
                  backgroundColor: theme.palette.mode === 'dark' ? 'rgba(0, 0, 0, 0.05)' : 'grey.100',
                }}
              >
                {SocialIcons.map((sicon) => {
                  return <IconButton key={sicon.name}>{sicon.icon}</IconButton>;
                })}
              </Box>
            </BlankCard>
          </Grid>
        ))}
      </Grid>
    </ParentCard>)
  );
};

export default ProfileCard;
