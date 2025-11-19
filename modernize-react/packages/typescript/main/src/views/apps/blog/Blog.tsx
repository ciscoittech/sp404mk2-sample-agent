// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import React from 'react';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import BlogListing from 'src/components/apps/blog/BlogListing';
import { BlogProvider } from "src/context/BlogContext"

const Blog = () => {
  const BCrumb = [
    {
      to: '/',
      title: 'Home',
    },
    {
      title: 'Blog',
    },
  ];
  return (

    <BlogProvider>
      <PageContainer title="Blog" description="this is Blog page">
        <Breadcrumb title="Blog app" items={BCrumb} />
        {/* ------------------------------------------- */}
        {/* Blog Listing */}
        {/* ------------------------------------------- */}
        <BlogListing />
      </PageContainer>
    </BlogProvider>

  );
};

export default Blog;
