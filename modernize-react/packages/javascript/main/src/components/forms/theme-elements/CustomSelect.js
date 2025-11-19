import React from 'react';
import { Select } from '@mui/material';
import { styled } from '@mui/material/styles';

const CustomSelect = styled((props) => <Select {...props} />)();

export default CustomSelect;
