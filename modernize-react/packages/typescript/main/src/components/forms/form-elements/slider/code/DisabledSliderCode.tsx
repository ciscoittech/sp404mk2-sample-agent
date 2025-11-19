import CodeDialog from "src/components/shared/CodeDialog";
const DisabledSliderCode = () => {
    return (
        <>
            <CodeDialog>
                {`
"use client";
import * as React from 'react';
import { Slider } from '@mui/material';

<Slider disabled defaultValue={30}  />
`}
            </CodeDialog>
        </>
    );
};

export default DisabledSliderCode;