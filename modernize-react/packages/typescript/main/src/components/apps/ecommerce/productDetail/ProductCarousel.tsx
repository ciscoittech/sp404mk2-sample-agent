import React, { useContext, useEffect, useRef } from 'react';
import { Box } from '@mui/material';
import { useParams } from 'react-router';

//Carousel slider for product
import Slider from 'react-slick';
import 'slick-carousel/slick/slick.css';
import 'slick-carousel/slick/slick-theme.css';
import './Carousel.css';

//Carousel slider data
import SliderData from './SliderData';

import { ProductContext } from "src/context/EcommerceContext";


const ProductCarousel = () => {
  const { products } = useContext(ProductContext);
  const [state, setState] = React.useState<any>({ nav1: null, nav2: null });

  const { nav1, nav2 } = state;

  const { id } = useParams();

  const slider1 = useRef(null);
  const slider2 = useRef(null);

  useEffect(() => {
    setState({
      nav1: slider1.current,
      nav2: slider2.current,
    });
  }, []);

  // Find the product by Id
  const product = products.find((p) => p.id === Number(id));
  const getProductImage = product ? product.photo : '';


  const settings = {
    focusOnSelect: true,
    infinite: true,
    slidesToShow: 5,
    arrows: false,
    swipeToSlide: true,
    slidesToScroll: 1,
    centerMode: true,
    className: 'centerThumb',
    speed: 500,
  };

  return (
    <Box>
      <Slider asNavFor={nav2} ref={(slider: any) => (slider1.current = slider)}>
        <Box>
          <img
            src={getProductImage}
            alt={getProductImage}
            width="100%"
            style={{ borderRadius: '5px' }}
          />
        </Box>
        {SliderData.map((step) => (
          <Box key={step.id}>
            <img
              src={step.imgPath}
              alt={step.imgPath}
              width="100%"
              style={{ borderRadius: '5px' }}
            />
          </Box>
        ))}
      </Slider>
      <Slider asNavFor={nav1} ref={(slider: any) => (slider2.current = slider)} {...settings}>
        <Box sx={{ p: 1, cursor: 'pointer' }}>
          <img
            src={getProductImage}
            alt={getProductImage}
            width="100%"
            style={{ borderRadius: '5px' }}
          />
        </Box>
        {SliderData.map((step) => (
          <Box key={step.id} sx={{ p: 1, cursor: 'pointer' }}>
            <img
              src={step.imgPath}
              alt={step.imgPath}
              width="100%"
              style={{ borderRadius: '5px' }}
            />
          </Box>
        ))}
      </Slider>
    </Box>
  );
};

export default ProductCarousel;
