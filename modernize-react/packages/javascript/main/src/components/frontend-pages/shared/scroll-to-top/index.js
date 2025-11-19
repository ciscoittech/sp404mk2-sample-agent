import React, { useEffect, useState } from 'react';
import { IconArrowUp } from '@tabler/icons';
import { Fab } from '@mui/material';


const ScrollToTop = () => {
    const [isVisible, setIsVisible] = useState(false);

    // Function to handle scroll to top
    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth' // Smooth scrolling
        });
    };

    // Function to handle showing/hiding the button on scroll
    const toggleVisibility = () => {
        if (window.pageYOffset > 300) {
            setIsVisible(true);
        } else {
            setIsVisible(false);
        }
    };

    useEffect(() => {
        window.addEventListener('scroll', toggleVisibility);

        return () => {
            window.removeEventListener('scroll', toggleVisibility);
        };
    }, []);

    return (
        <> {isVisible ? <Fab color='primary' onClick={scrollToTop} sx={{
            position: 'fixed',
            right: '30px',
            bottom: '30px'
        }}>
            <IconArrowUp size={24} />
        </Fab> : null}</>

    );
};

export default ScrollToTop;
