import {
  CardContent,
  Box,
  Stack,
  Avatar,
  Grid,
  Typography,
  Chip,
  TextField,
  InputAdornment,
  Divider,
  IconButton,
} from '@mui/material';
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext, useEffect } from 'react';
import BlankCard from 'src/components/shared/BlankCard';
import { UserDataContext } from "src/context/UserDataContext";

import {
  IconBrandFacebook,
  IconBrandGithub,
  IconBrandInstagram,
  IconBrandTwitter,
  IconSearch,
} from '@tabler/icons-react';


interface socialType {
  name: string;
  icon: React.ReactElement;
}

const SocialIcons: socialType[] = [
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

const FriendsCard = () => {
  const { followers, setSearch }: any = useContext(UserDataContext);


  return (<>
    <Grid container spacing={3}>
      <Grid
        size={{
          sm: 12,
          lg: 12
        }}>
        <Stack direction="row" alignItems={'center'} mt={2}>
          <Box>
            <Typography variant="h3">
              Friends &nbsp;
              <Chip label={followers.length} color="secondary" size="small" />
            </Typography>
          </Box>
          <Box ml="auto">
            <TextField
              id="outlined-search"
              placeholder="Search Friends"
              size="small"
              type="search"
              variant="outlined"
              fullWidth
              onChange={(e) => setSearch(e.target.value)}
              slotProps={{
                input: {
                  startAdornment: (
                    <InputAdornment position="start">
                      <IconSearch size="14" />
                    </InputAdornment>
                  ),
                },

                htmlInput: { 'aria-label': 'Search Followers' }
              }} />
          </Box>
        </Stack>
      </Grid>
      {followers.map((profile: any) => {
        return (
          (<Grid
            key={profile.id}
            size={{
              xs: 12,
              lg: 4
            }}>
            <BlankCard className="hoverCard">
              <CardContent>
                <Stack direction={'column'} gap={2} alignItems="center">
                  <Avatar
                    alt="Remy Sharp"
                    src={profile.avatar}
                    sx={{ width: '80px', height: '80px' }}
                  />
                  <Box textAlign={'center'}>
                    <Typography variant="h5">{profile.name}</Typography>
                    <Typography variant="caption">{profile.role}</Typography>
                  </Box>
                </Stack>
              </CardContent>
              <Divider />
              <Box p={2} py={1} textAlign={'center'} sx={{ backgroundColor: 'grey.100' }}>
                {SocialIcons.map((sicon) => {
                  return <IconButton key={sicon.name}>{sicon.icon}</IconButton>;
                })}
              </Box>
            </BlankCard>
          </Grid>)
        );
      })}
    </Grid>
  </>);
};

export default FriendsCard;
