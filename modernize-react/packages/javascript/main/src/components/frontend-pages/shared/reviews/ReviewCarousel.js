import React, { useState, useRef } from 'react';
import { Avatar, CardContent, Divider, Stack, Typography, Box, Paper } from '@mui/material';
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import { IconChevronLeft, IconChevronRight } from '@tabler/icons';

import user1 from 'src/assets/images/profile/user-1.jpg';
import user2 from 'src/assets/images/profile/user-2.jpg';
import user3 from 'src/assets/images/profile/user-3.jpg';
import user4 from 'src/assets/images/profile/user-4.jpg';
import user5 from 'src/assets/images/profile/user-5.jpg';

function SampleNextArrow(props) {
  const { className, onClick } = props;
  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      className={className}
      sx={{
        cursor: 'pointer',
        position: 'absolute',
        left: '125px',
        zIndex: 1,
        bottom: '45px',
        right: 0,
        backgroundColor: (theme) => theme.palette.grey[100],
        width: '32px',
        height: '32px',
        borderRadius: '50%',
      }}
      onClick={onClick}
    >
      <IconChevronRight strokeWidth={1.5} size={20} />
    </Box>
  );
}

function SamplePrevArrow(props) {
  const { className, onClick } = props;
  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      className={className}
      sx={{
        cursor: 'pointer',
        position: 'absolute',
        left: '48px',
        zIndex: 1,
        bottom: '45px',
        right: '60px',
        backgroundColor: (theme) => theme.palette.grey[100],
        width: '32px',
        height: '32px',
        borderRadius: '50%',
      }}
      onClick={onClick}
    >
      <IconChevronLeft strokeWidth={1.5} size={20} />
    </Box>
  );
}

const Reviews = [
  {
    id: 1,
    img: user1,
    name: 'Jenny Wilson',
    text: 'This template is great, UI-rich and up-to-date. Although it is pretty much complete, I suggest to improve a bit of documentation. Thanks & Highly recommended!',
  },
  {
    id: 2,
    img: user2,
    name: 'Jenny Wilson',
    text: 'This template is great, UI-rich and up-to-date. Although it is pretty much complete, I suggest to improve a bit of documentation. Thanks & Highly recommended!',
  },
  {
    id: 3,
    img: user3,
    name: 'Jenny Wilson',
    text: 'This template is great, UI-rich and up-to-date. Although it is pretty much complete, I suggest to improve a bit of documentation. Thanks & Highly recommended!',
  },
  {
    id: 4,
    img: user4,
    name: 'Jenny Wilson',
    text: 'This template is great, UI-rich and up-to-date. Although it is pretty much complete, I suggest to improve a bit of documentation. Thanks & Highly recommended!',
  },
  {
    id: 5,
    img: user5,
    name: 'Jenny Wilson',
    text: 'This template is great, UI-rich and up-to-date. Although it is pretty much complete, I suggest to improve a bit of documentation. Thanks & Highly recommended!',
  },
];

const ReviewCarousel = () => {
  const [oldSlide, setOldSlide] = useState(0);
  const [activeSlide, setActiveSlide] = useState(1);
  const [activeSlide2, setActiveSlide2] = useState(1);

  let sliderRef = useRef(null);

  const settings = {
    dots: false,
    fade: true,
    infinite: true,
    speed: 500,

    slidesToShow: 1,
    slidesToScroll: 1,
    nextArrow: <SampleNextArrow />,
    prevArrow: <SamplePrevArrow />,
    beforeChange: (current, next) => {
      setOldSlide(current);
      setActiveSlide(next);
    },
    afterChange: (current) => setActiveSlide2(current),
  };

  return (
    <>
      <Slider
        ref={(slider) => {
          sliderRef = slider;
        }}
        {...settings}
      >
        {Reviews.map((review, i) => (
          <div key={i}>
            <Paper variant="outlined" sx={{ borderRadius: '16px' }}>
              <CardContent sx={{ p: '48px !important' }}>
                <Typography variant="h4" lineHeight={1.4} mb={3} fontWeight={600} fontSize="24px">
                  Features avaibility
                </Typography>
                <Stack direction="row" alignItems="center" gap={3} mb={3}>
                  <Avatar src={review.img} alt="user" />
                  <Typography variant="body1" fontWeight={600}>
                    {review.name}
                  </Typography>
                </Stack>
                <Typography variant="body1" lineHeight={1.8} mb={2}>
                  {review.text}
                </Typography>
                <Divider />

                <Typography fontSize="14px" fontWeight={500} ml={5} mt={3}>
                  {' '}
                  {activeSlide} / {Reviews.length}
                </Typography>
              </CardContent>
            </Paper>
          </div>
        ))}
      </Slider>
    </>
  );
};

export default ReviewCarousel;
