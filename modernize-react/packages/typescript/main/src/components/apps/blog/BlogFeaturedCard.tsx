

import { Link } from 'react-router';
import {
  CardContent,
  Stack,
  Avatar,
  Typography,
  Chip,
  Grid,
  Tooltip,
  Box,
  alpha,
  styled,

} from '@mui/material';
import { IconEye, IconMessage2, IconPoint } from '@tabler/icons-react';
import { format } from 'date-fns';

import BlankCard from '../../shared/BlankCard';
import { BlogPostType } from 'src/types/apps/blog';
import { useContext, useEffect } from 'react';
import { BlogContext, BlogContextProps } from 'src/context/BlogContext/index';

const CoverImgStyle = styled(CardContent)({
  position: 'absolute',
  top: '0',
  left: '0',
  zIndex: 1,
  width: '100%',
  height: '100%',
  color: 'white',
});
const CoverBox = styled(Box)({
  top: 0,
  content: "''",
  width: '100%',
  height: '100%',
  position: 'absolute',
});

interface Btype {
  post: BlogPostType;
  index: number;
}

const BlogFeaturedCard = ({ post, index }: Btype) => {


  const { coverImg, title, view, comments, category, author, createdAt }: any = post;
  const linkTo = title
    .toLowerCase()
    .replace(/ /g, '-')
    .replace(/[^\w-]+/g, '');
  const mainPost = index === 0;

  const CoverImgBg = styled(BlankCard)({
    p: 0,
    height: '400px',
    position: 'relative',
    background: `url(${coverImg}) no-repeat center`,
    backgroundSize: 'cover',
  });

  const { setLoading }: BlogContextProps = useContext(BlogContext);

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 700);

    return () => clearTimeout(timer);
  }, []);

  return (<>
    {post ? (
      <Grid
        display="flex"
        alignItems="stretch"
        size={{
          xs: 12,
          lg: mainPost ? 8 : 4,
          md: 12,
          sm: 12
        }}>
        <CoverImgBg className="hoverCard">
          <>
            <Typography
              component={Link}
              to={`/frontend-pages/blog/detail/${linkTo}`}
            >
              <CoverBox
                sx={{ backgroundColor: (theme) => alpha(theme.palette.grey[900], 0.6) }}
              />
            </Typography>
            <CoverImgStyle>
              <Box
                height={'100%'}
                display={'flex'}
                justifyContent="space-between"
                flexDirection="column"
              >
                <Box>
                  <Stack direction="row">
                    <Tooltip title={author?.name} placement="top">
                      <Avatar aria-label="recipe" src={author?.avatar}></Avatar>
                    </Tooltip>
                    <Chip
                      sx={{ marginLeft: 'auto' }}
                      label={category}
                      size="small"
                      color="primary"
                    ></Chip>
                  </Stack>
                </Box>
                <Box>
                  <Box my={3}>
                    <Typography
                      gutterBottom
                      variant="h3"
                      color="inherit"
                      sx={{ textDecoration: 'none' }}
                      component={Link}
                      to={`/frontend-pages/blog/detail/${linkTo}`}

                    >
                      {title}
                    </Typography>
                  </Box>
                  <Stack direction="row" gap={3} alignItems="center">
                    <Stack direction="row" gap={1} alignItems="center">
                      <IconEye size="18" /> {view}
                    </Stack>
                    <Stack direction="row" gap={1} alignItems="center">
                      <IconMessage2 size="18" /> {comments?.length}
                    </Stack>

                    <Stack direction="row" ml="auto" alignItems="center">
                      <IconPoint size="16" />
                      <small>{format(new Date(createdAt), 'E, MMM d')}</small>
                    </Stack>
                  </Stack>
                </Box>
              </Box>
            </CoverImgStyle>
          </>
        </CoverImgBg>
      </Grid>
    ) : (
      ''
    )}
  </>);
};

export default BlogFeaturedCard;
