// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import * as React from 'react';
import { Grid, Rating, Box, Stack } from '@mui/material';
import Breadcrumb from 'src/layouts/full/shared/breadcrumb/Breadcrumb';
import PageContainer from 'src/components/container/PageContainer';
import ParentCard from 'src/components/shared/ParentCard';
import ChildCard from 'src/components/shared/ChildCard';
import { IconContainerProps } from '@mui/material/Rating';
import { IconStar } from '@tabler/icons-react';
import { styled } from '@mui/material/styles';
import FavoriteIcon from '@mui/icons-material/Favorite';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import SentimentVeryDissatisfiedIcon from '@mui/icons-material/SentimentVeryDissatisfied';
import SentimentDissatisfiedIcon from '@mui/icons-material/SentimentDissatisfied';
import SentimentSatisfiedIcon from '@mui/icons-material/SentimentSatisfied';
import SentimentSatisfiedAltIcon from '@mui/icons-material/SentimentSatisfiedAltOutlined';
import SentimentVerySatisfiedIcon from '@mui/icons-material/SentimentVerySatisfied';

const BCrumb = [
  {
    to: '/',
    title: 'Home',
  },
  {
    title: 'Rating',
  },
];
const labels: { [index: string]: string } = {
  0.5: 'Useless',
  1: 'Useless+',
  1.5: 'Poor',
  2: 'Poor+',
  2.5: 'Ok',
  3: 'Ok+',
  3.5: 'Good',
  4: 'Good+',
  4.5: 'Excellent',
  5: 'Excellent+',
};
function getLabelText(value: number) {
  return `${value} Star${value !== 1 ? 's' : ''}, ${labels[value]}`;
}
const StyledRating = styled(Rating)({
  '& .MuiRating-iconFilled': {
    color: '#ff6d75',
  },
  '& .MuiRating-iconHover': {
    color: '#ff3d47',
  },
});
const RadioRating = styled(Rating)(({ theme }) => ({
  '& .MuiRating-iconEmpty .MuiSvgIcon-root': {
    color: theme.palette.action.disabled,
  },
}));
const customIcons: {
  [index: string]: {
    icon: React.ReactElement;
    label: string;
  };
} = {
  1: {
    icon: <SentimentVeryDissatisfiedIcon color="error" />,
    label: 'Very Dissatisfied',
  },
  2: {
    icon: <SentimentDissatisfiedIcon color="error" />,
    label: 'Dissatisfied',
  },
  3: {
    icon: <SentimentSatisfiedIcon color="warning" />,
    label: 'Neutral',
  },
  4: {
    icon: <SentimentSatisfiedAltIcon color="success" />,
    label: 'Satisfied',
  },
  5: {
    icon: <SentimentVerySatisfiedIcon color="success" />,
    label: 'Very Satisfied',
  },
};
function IconContainer(props: IconContainerProps) {
  const { value, ...other } = props;

  return <span {...other}>{customIcons[value].icon}</span>;
}

const MuiRating = () => {
  const [value, setValue] = React.useState<number | null>(2);
  const [hover, setHover] = React.useState(-1);

  return (
    (<PageContainer title="Rating" description="this is Rating page">
      {/* breadcrumb */}
      <Breadcrumb title="Rating" items={BCrumb} />
      {/* end breadcrumb */}
      <ParentCard title="Rating">
        <Grid container spacing={3}>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Controlled">
              <Rating
                name="simple-controlled"
                value={value}
                // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                // @ts-ignore
                onChange={(event, newValue) => {
                  setValue(newValue);
                }}
              />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Read Only">
              <Rating name="read-only" value={value} readOnly />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Disabled">
              <Rating name="disabled" value={value} disabled />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="No Rating">
              <Rating name="no-value" value={null} />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Rating precision">
              <Rating name="half-rating" defaultValue={2.5} precision={0.5} />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Hover feedback">
              <Stack direction="row" spacing={2} alignItems="center">
                <Rating
                  name="hover-feedback"
                  value={value}
                  precision={0.5}
                  getLabelText={getLabelText}
                  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                  // @ts-ignore
                  onChange={(event, newValue) => {
                    setValue(newValue);
                  }}
                  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                  // @ts-ignore
                  onChangeActive={(event, newHover) => {
                    setHover(newHover);
                  }}
                  emptyIcon={<IconStar width={20} style={{ opacity: 0.55 }} fontSize="inherit" />}
                />
                {value !== null && <Box>{labels[hover !== -1 ? hover : value]}</Box>}
              </Stack>
            </ChildCard>
          </Grid>

          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Custom Icon Set">
              <Stack spacing={2}>
                <StyledRating
                  name="customized-color"
                  defaultValue={2}
                  getLabelText={(value) => `${value} Heart${value !== 1 ? 's' : ''}`}
                  precision={0.5}
                  icon={<FavoriteIcon fontSize="inherit" />}
                  emptyIcon={<FavoriteBorderIcon fontSize="inherit" />}
                />
              </Stack>
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="10 Stars">
              <Rating name="customized-10" defaultValue={2} max={10} />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Radio Group">
              <RadioRating
                name="highlight-selected-only"
                defaultValue={2}
                IconContainerComponent={IconContainer}
                getLabelText={(value: number) => customIcons[value].label}
                highlightSelectedOnly
              />
            </ChildCard>
          </Grid>
          <Grid
            display="flex"
            alignItems="stretch"
            size={{
              xs: 12,
              lg: 4,
              sm: 6
            }}>
            <ChildCard title="Sizes">
              <Stack spacing={2}>
                <Rating name="size-small" defaultValue={2} size="small" />
                <Rating name="size-medium" defaultValue={2} />
                <Rating name="size-large" defaultValue={2} size="large" />
              </Stack>
            </ChildCard>
          </Grid>
        </Grid>
      </ParentCard>
    </PageContainer>)
  );
};
export default MuiRating;
