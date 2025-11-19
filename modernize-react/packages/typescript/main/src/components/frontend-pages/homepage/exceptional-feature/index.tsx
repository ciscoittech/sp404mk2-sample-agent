import { Box, Grid, Typography, Container } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useTheme } from '@mui/material/styles';

import IconColor from 'src/assets/images/frontend-pages/icons/icon-color.svg';
import IconSidebar from 'src/assets/images/frontend-pages/icons/icon-sidebar.svg';
import IconPages from 'src/assets/images/frontend-pages/icons/icon-pages.svg';
import IconComponents from 'src/assets/images/frontend-pages/icons/icon-components.svg';
import IconFramework from 'src/assets/images/frontend-pages/icons/icon-framework.svg';
import IconIcons from 'src/assets/images/frontend-pages/icons/icon-icons.svg';
import IconResponsive from 'src/assets/images/frontend-pages/icons/icon-responsive.svg';
import IconSass from 'src/assets/images/frontend-pages/icons/icon-sass.svg';
import IconCustomize from 'src/assets/images/frontend-pages/icons/icon-customize.svg';
import IconChart from 'src/assets/images/frontend-pages/icons/icon-chart.svg';
import IconTable from 'src/assets/images/frontend-pages/icons/icon-table.svg';
import IconUpdate from 'src/assets/images/frontend-pages/icons/icon-update.svg';
import IconSupport from 'src/assets/images/frontend-pages/icons/icon-support.svg';

const StyledAnimationFeature = styled(Box)(() => ({
  width: '100%',
  overflowX: 'hidden',
  whiteSpace: 'nowrap',
  boxSizing: 'border-box',
}));







const slide1 = [
  {
    icon: IconColor,
    text: '6 Theme Colors',
  },
  {
    icon: IconSidebar,
    text: 'Dark & Light Sidebar',
  },
  {
    icon: IconPages,
    text: '65+ Page Templates',
  },
  {
    icon: IconComponents,
    text: '50+ UI Components',
  },
  {
    icon: IconColor,
    text: '6 Theme Colors',
  },
  {
    icon: IconSidebar,
    text: 'Dark & Light Sidebar',
  },
  {
    icon: IconPages,
    text: '65+ Page Templates',
  },
  {
    icon: IconComponents,
    text: '50+ UI Components',
  },
  {
    icon: IconColor,
    text: '6 Theme Colors',
  },
  {
    icon: IconSidebar,
    text: 'Dark & Light Sidebar',
  },
  {
    icon: IconPages,
    text: '65+ Page Templates',
  },
  {
    icon: IconComponents,
    text: '50+ UI Components',
  },
];

const slide2 = [
  {
    icon: IconFramework,
    text: 'Material Ui',
  },
  {
    icon: IconIcons,
    text: '3400+ Icon',
  },
  {
    icon: IconResponsive,
    text: 'Fully Responsive',
  },
  {
    icon: IconSass,
    text: 'Sassbase CSS',
  },
  {
    icon: IconFramework,
    text: 'Material Ui',
  },
  {
    icon: IconIcons,
    text: '3400+ Icon',
  },
  {
    icon: IconResponsive,
    text: 'Fully Responsive',
  },
  {
    icon: IconSass,
    text: 'Sassbase CSS',
  },
  {
    icon: IconFramework,
    text: 'Material Ui',
  },
  {
    icon: IconIcons,
    text: '3400+ Icon',
  },
  {
    icon: IconResponsive,
    text: 'Fully Responsive',
  },
  {
    icon: IconSass,
    text: 'Sassbase CSS',
  },
];

const slide3 = [
  {
    icon: IconCustomize,
    text: 'Easy to Customize',
  },
  {
    icon: IconChart,
    text: 'Lots of Chart Options',
  },
  {
    icon: IconTable,
    text: 'Lots of Table Examples',
  },
  {
    icon: IconUpdate,
    text: 'Regular Updates',
  },
  {
    icon: IconSupport,
    text: 'Dedicated Support',
  },
  {
    icon: IconCustomize,
    text: 'Easy to Customize',
  },
  {
    icon: IconChart,
    text: 'Lots of Chart Options',
  },
  {
    icon: IconTable,
    text: 'Lots of Table Examples',
  },
  {
    icon: IconUpdate,
    text: 'Regular Updates',
  },
  {
    icon: IconSupport,
    text: 'Dedicated Support',
  },
  {
    icon: IconCustomize,
    text: 'Easy to Customize',
  },
  {
    icon: IconChart,
    text: 'Lots of Chart Options',
  },
  {
    icon: IconTable,
    text: 'Lots of Table Examples',
  },
  {
    icon: IconUpdate,
    text: 'Regular Updates',
  },
  {
    icon: IconSupport,
    text: 'Dedicated Support',
  },
];

const ExceptionalFeature = () => {
  const theme = useTheme();

  const StyledAnimationContent = styled(Box)(() => ({
    animation: theme.direction == 'ltr' ? 'marquee 25s linear infinite' : 'marqueeRtl 45s linear infinite'
  }));

  const StyledAnimationContent2 = styled(Box)(() => ({
    animation: theme.direction == 'ltr' ? 'marquee2 25s linear infinite' : 'marquee2Rtl 45s linear infinite'
  }));


  const StyledFeatureBox = styled(Box)(() => ({
    boxShadow: theme.shadows[10],
    backgroundColor: theme.palette.background.default,
    minHeight: '72px',
    width: '315px',
    borderRadius: '16px',
    marginTop: '15px',
    marginBottom: '15px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    flexShrink: 0,
  }));

  return (<>
    <Container
      sx={{
        maxWidth: '1400px !important',
      }}
    >
      <Box
        bgcolor="primary.light"
        borderRadius="24px"
        sx={{
          py: {
            xs: '40px',
            lg: '70px',
          },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={3} alignItems="center" justifyContent="center">
            <Grid
              size={{
                xs: 12,
                lg: 7,
                sm: 9
              }}>
              <Typography
                variant="h4"
                mb="55px"
                textAlign="center"
                fontWeight={700}
                fontSize="40px"
                lineHeight="1.2"
                sx={{
                  fontSize: {
                    lg: '40px',
                    xs: '30px',
                  },
                }}
              >
                Enjoy unparalleled features & exceptional flexibility.
              </Typography>
            </Grid>
          </Grid>
        </Container>

        <StyledAnimationFeature>
          <StyledAnimationContent display="flex" gap="30px">
            {slide1.map((slide, i) => (
              <StyledFeatureBox key={i}>
                <img src={slide.icon} alt="color" width={24} height={24} />
                <Typography fontSize="15px" fontWeight={600}>
                  {slide.text}
                </Typography>
              </StyledFeatureBox>
            ))}
          </StyledAnimationContent>
        </StyledAnimationFeature>

        <StyledAnimationFeature>
          <StyledAnimationContent2 display="flex" gap="30px">
            {slide2.map((slide, i) => (
              <StyledFeatureBox key={i}>
                <img src={slide.icon} alt="color" width={24} height={24} />
                <Typography fontSize="15px" fontWeight={600}>
                  {slide.text}
                </Typography>
              </StyledFeatureBox>
            ))}
          </StyledAnimationContent2>
        </StyledAnimationFeature>

        <StyledAnimationFeature>
          <StyledAnimationContent display="flex" gap="30px">
            {slide3.map((slide, i) => (
              <StyledFeatureBox key={i}>
                <img src={slide.icon} alt="color" width={24} height={24} />
                <Typography fontSize="15px" fontWeight={600}>
                  {slide.text}
                </Typography>
              </StyledFeatureBox>
            ))}
          </StyledAnimationContent>
        </StyledAnimationFeature>
      </Box>
    </Container>
  </>);
};

export default ExceptionalFeature;
