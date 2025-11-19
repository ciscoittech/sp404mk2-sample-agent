import React from 'react';
import { Box, FormControlLabel } from '@mui/material';
import CustomRadio from '../../theme-elements/CustomRadio';

const ColorLabelRadio = () => {
    return (
        <Box textAlign="center">
            <FormControlLabel
                value="end"
                control={<CustomRadio bgcolor="primary" checked />}
                label="Primary"
                labelPlacement="end"
            />
            <FormControlLabel
                value="end"
                control={<CustomRadio bgcolor="secondary" checked />}
                label="Secondary"
                labelPlacement="end"
            />
            <FormControlLabel
                value="end"
                control={<CustomRadio bgcolor="success" checked />}
                label="Success"
                labelPlacement="end"
            />

            <FormControlLabel
                value="end"
                control={<CustomRadio bgcolor="error" checked />}
                label="Error"
                labelPlacement="end"
            />

            <FormControlLabel
                value="end"
                control={<CustomRadio bgcolor="warning" checked />}
                label="Warning"
                labelPlacement="end"
            />
        </Box>
    );
};

export default ColorLabelRadio;
