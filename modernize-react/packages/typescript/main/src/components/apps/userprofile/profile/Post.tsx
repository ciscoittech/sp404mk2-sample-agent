import { Grid } from '@mui/material';

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext, useEffect } from 'react';

import PostItem from './PostItem';
import { PostTextBox } from './PostTextBox';
import { UserDataContext } from "src/context/UserDataContext";


const Post = () => {
  const { posts }: any = useContext(UserDataContext);

  return (
    (<Grid container spacing={3}>
      <Grid
        size={{
          sm: 12
        }}>
        <PostTextBox />
      </Grid>
      {posts.map((posts: any) => {
        return (
          (<Grid
            key={posts.id}
            size={{
              sm: 12
            }}>
            <PostItem post={posts} />
          </Grid>)
        );
      })}
    </Grid>)
  );
};

export default Post;

