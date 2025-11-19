import PageContainer from 'src/components/container/PageContainer';
import HeaderAlert from '../../../components/frontend-pages/shared/header/HeaderAlert';
import HpHeader from '../../../components/frontend-pages/shared/header/HpHeader';
import C2a from '../../../components/frontend-pages/shared/c2a';
import Footer from '../../../components/frontend-pages/shared/footer';
import Banner from '../../../components/frontend-pages/blog/banner';
import ScrollToTop from '../../../components/frontend-pages/shared/scroll-to-top';
import BlogListing from 'src/components/apps/blog/BlogListing';
import { Container } from '@mui/system';
import { BlogProvider } from 'src/context/BlogContext';

const BlogPage = () => {
  return (
    <>
      <BlogProvider>
        <PageContainer title="Blog" description="this is Blog">
          <HeaderAlert />
          <HpHeader />
          <Banner />
          <Container maxWidth="lg" sx={{ mt: 5 }}>
            <BlogListing />
          </Container>
          <C2a />
          <Footer />
          <ScrollToTop />
        </PageContainer>
      </BlogProvider>
    </>
  );
};

export default BlogPage;
