// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React, { useContext, useEffect } from 'react';
import { Grid } from '@mui/material';
import BlogCard from './BlogCard';
import { orderBy } from 'lodash';
import { BlogContext } from "src/context/BlogContext/index";
import BlogFeaturedCard from './BlogFeaturedCard';
import { BlogPostType } from 'src/types/apps/blog';

const BlogListing = () => {

  const { posts, sortBy } = useContext(BlogContext);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const filterBlogs = (posts: BlogPostType[], sortBy: string) => {
    // SORT BY

    if (sortBy === 'newest') {
      posts = orderBy(posts, ['createdAt'], ['desc']);
    }
    if (sortBy === 'oldest') {
      posts = orderBy(posts, ['createdAt'], ['asc']);
    }
    if (sortBy === 'popular') {
      posts = orderBy(posts, ['view'], ['desc']);
    }
    return posts.filter((post) => !post.featured);


  };

  const filterFeaturedpost = (posts: BlogPostType[]) => {
    return (posts = posts.filter((t) => t.featured));
  };

  const blogPosts = filterBlogs(posts, sortBy);
  const featuredPosts = filterFeaturedpost(posts);

  return (
    (<Grid container spacing={3}>
      {featuredPosts.map((post, index) => {
        return <BlogFeaturedCard index={index} post={post} key={post.title} />;
      })}
      {blogPosts.map((post) => {
        return <BlogCard post={post} key={post.id} />;
      })}
      <Grid
        mt={3}
        size={{
          lg: 12,
          sm: 12
        }}>

      </Grid>
    </Grid>)
  );
};

export default BlogListing;
