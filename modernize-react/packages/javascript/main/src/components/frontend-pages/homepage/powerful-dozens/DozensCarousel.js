import React from 'react';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import './carousel.css';
import { Box } from '@mui/material';

import Demo1 from 'src/assets/images/landingpage/demos/demo-main.jpg';
import Demo2 from 'src/assets/images/landingpage/demos/demo-dark.jpg';
import Demo3 from 'src/assets/images/landingpage/demos/demo-rtl.jpg';
import Demo4 from 'src/assets/images/landingpage/demos/demo-horizontal.jpg';

import App1 from 'src/assets/images/landingpage/apps/app-chat.jpg';
import App2 from 'src/assets/images/landingpage/apps/app-email.jpg';
import { NavLink } from 'react-router';

const DozensCarousel = () => {
  const settings = {
    dots: false,
    arrows: false,
    infinite: true,
    speed: 4500,
    autoplay: true,
    centerMode: false,
    slidesToShow: 4,
    slidesToScroll: 4,
    responsive: [
      {
        breakpoint: 1024,
        settings: {
          slidesToShow: 2,
          slidesToScroll: 2,
        },
      },
      {
        breakpoint: 480,
        settings: {
          slidesToShow: 1,
          slidesToScroll: 1,
        },
      },
    ],
  };

  return (
    <Slider {...settings} className="dozenscarousel" style={{ marginLeft: '15px' }}>
      <div>
        <Box
          width={380}
          height={300}
          borderRadius="16px"
          sx={{ boxShadow: (theme) => theme.shadows[10], padding: '0 30px 16px' }}
        >
          <NavLink to="https://modernize-react.adminmart.com/dashboards/modern">
            <img
              src={Demo1}
              alt="user-img"
              width={380}
              height={300}
              style={{ borderRadius: '16px' }}
            />
          </NavLink>
        </Box>
      </div>
      <div>
        <Box
          width={380}
          height={300}
          borderRadius="16px"
          sx={{ boxShadow: (theme) => theme.shadows[10], padding: '0 30px 16px' }}
        >
          <NavLink to="https://modernize-react-dark.netlify.app/dashboards/ecommerce">
            <img
              src={Demo2}
              alt="user-img"
              width={380}
              height={300}
              style={{ borderRadius: '16px' }}
            />
          </NavLink>
        </Box>
      </div>
      <div>
        <Box
          width={380}
          height={300}
          borderRadius="16px"
          sx={{ boxShadow: (theme) => theme.shadows[10], padding: '0 30px 16px' }}
        >
          <NavLink to="https://modernize-react-rtl.netlify.app/dashboards/modern">
            <img
              src={Demo3}
              alt="user-img"
              width={380}
              height={300}
              style={{ borderRadius: '16px' }}
            />
          </NavLink>
        </Box>
      </div>
      <div>
        <Box
          width={380}
          height={300}
          borderRadius="16px"
          sx={{ boxShadow: (theme) => theme.shadows[10], padding: '0 30px 16px' }}
        >
          <NavLink to="https://modernize-react-horizontal.netlify.app/dashboards/modern">
            <img
              src={Demo4}
              alt="user-img"
              width={380}
              height={300}
              style={{ borderRadius: '16px' }}
            />
          </NavLink>
        </Box>
      </div>
      <div>
        <Box
          width={380}
          height={300}
          borderRadius="16px"
          sx={{ boxShadow: (theme) => theme.shadows[10], padding: '0 30px 16px' }}
        >
          <NavLink to="https://modernize-react.adminmart.com/apps/chats">
            <img
              src={App1}
              alt="user-img"
              width={380}
              height={300}
              style={{ borderRadius: '16px' }}
            />
          </NavLink>
        </Box>
      </div>
      <div>
        <Box
          width={380}
          height={300}
          borderRadius="16px"
          sx={{ boxShadow: (theme) => theme.shadows[10], padding: '0 30px 16px' }}
        >
          <NavLink to="https://modernize-react.adminmart.com/apps/email">
            <img
              src={App2}
              alt="user-img"
              width={380}
              height={300}
              style={{ borderRadius: '16px' }}
            />
          </NavLink>
        </Box>
      </div>
    </Slider>
  );
};

export default DozensCarousel;
