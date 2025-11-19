// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import { Grid } from '@mui/material';
import PageContainer from 'src/components/container/PageContainer';
import ProfileBanner from 'src/components/apps/userprofile/profile/ProfileBanner';
import GalleryCard from 'src/components/apps/userprofile/gallery/GalleryCard';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import { UserDataProvider } from "src/context/UserDataContext/index";


const Gallery = () => {
  const BCrumb = [
    {
      to: '/',
      title: 'Home',
    },
    {
      title: 'Gallery',
    },
  ]
  return (
    <UserDataProvider>
      <PageContainer title="User Profile" description="this is User Profile page">
        <Breadcrumb title="User App" items={BCrumb} />
        <Grid container spacing={3}>
          <Grid
            size={{
              sm: 12
            }}>
            <ProfileBanner />
          </Grid>
          <Grid
            size={{
              sm: 12
            }}>
            <GalleryCard />
          </Grid>
        </Grid>
      </PageContainer>
    </UserDataProvider>
  );
};

export default Gallery;